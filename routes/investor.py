from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.project import Project
from models.investment import Investment
from models.transaction import Transaction
from models.setting import Setting
from routes.auth import role_required
import uuid
import decimal

investor_bp = Blueprint('investor', __name__)

@investor_bp.route('/dashboard')
@login_required
@role_required('investor')
def dashboard():
    investments = Investment.query.filter_by(investor_id=current_user.id).order_by(Investment.created_at.desc()).all()
    total_invested = sum(inv.investment_amount for inv in investments)
    return render_template('investor/dashboard.html', investments=investments, total_invested=total_invested)

@investor_bp.route('/invest/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('investor')
def invest(project_id):
    project = Project.query.get_or_404(project_id)
    if project.status != 'approved':
        flash('Project not available for investment.', 'danger')
        return redirect(url_for('main.index'))
        
    setting = Setting.query.first()
    platform_fee_percentage = setting.platform_fee_percentage if setting else decimal.Decimal('5.00')
        
    if request.method == 'POST':
        percentage_str = request.form.get('percentage')
        if not percentage_str:
            flash('Invalid percentage', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))
            
        percentage = decimal.Decimal(percentage_str)
        if percentage <= 0 or percentage > 100:
            flash('Percentage must be between 1 and 100', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))
            
        agreement = request.form.get('agreement')
        if not agreement:
            flash('You must accept the agreement.', 'danger')
            return redirect(url_for('investor.invest', project_id=project.id))

        # Calculation
        investment_amount = project.goal_amount * (percentage / decimal.Decimal('100.00'))
        
        if (project.raised_amount + investment_amount) > project.goal_amount:
            val = project.goal_amount - project.raised_amount
            flash(f'Investment exceeds the remaining goal amount! Maximum allowed is ${val}.', 'warning')
            return redirect(url_for('investor.invest', project_id=project.id))

        platform_fee = investment_amount * (platform_fee_percentage / decimal.Decimal('100.00'))
        net_amount = investment_amount - platform_fee

        # Show mock payment confirmation
        return render_template('investor/payment.html', 
                               project=project, 
                               percentage=percentage, 
                               investment_amount=investment_amount,
                               platform_fee=platform_fee,
                               net_amount=net_amount,
                               platform_fee_percentage=platform_fee_percentage)

    return render_template('investor/invest.html', project=project, platform_fee_percentage=platform_fee_percentage)

@investor_bp.route('/process_payment/<int:project_id>', methods=['POST'])
@login_required
@role_required('investor')
def process_payment(project_id):
    project = Project.query.get_or_404(project_id)
    percentage = decimal.Decimal(request.form.get('percentage'))
    
    setting = Setting.query.first()
    platform_fee_percentage = setting.platform_fee_percentage if setting else decimal.Decimal('5.00')
    
    investment_amount = project.goal_amount * (percentage / decimal.Decimal('100.00'))
    
    if (project.raised_amount + investment_amount) > project.goal_amount:
            flash('Investment exceeds the remaining goal amount!', 'warning')
            return redirect(url_for('investor.invest', project_id=project.id))
            
    platform_fee = investment_amount * (platform_fee_percentage / decimal.Decimal('100.00'))
    net_amount = investment_amount - platform_fee
    
    # Store investment
    inv = Investment(
        investor_id=current_user.id,
        project_id=project.id,
        percentage=percentage,
        investment_amount=investment_amount,
        platform_fee=platform_fee,
        net_amount=net_amount
    )
    db.session.add(inv)
    
    # Update project
    project.raised_amount += investment_amount
    
    # Store transaction
    txn_ref = str(uuid.uuid4())
    txn = Transaction(
        investor_id=current_user.id,
        project_id=project.id,
        amount=investment_amount,
        platform_fee=platform_fee,
        transferred_amount=net_amount,
        transaction_reference=txn_ref
    )
    db.session.add(txn)
    
    db.session.commit()
    
    flash('Payment successful! Investment recorded.', 'success')
    return render_template('investor/success.html', transaction=txn, project=project, net=net_amount, percentage=percentage)

@investor_bp.route('/history')
@login_required
@role_required('investor')
def history():
    transactions = Transaction.query.filter_by(investor_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template('investor/history.html', transactions=transactions)
