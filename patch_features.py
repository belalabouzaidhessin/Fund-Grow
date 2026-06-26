import os
import pymysql

base_dir = "D:/fundgrow"

project_model_path = os.path.join(base_dir, 'models/project.py')
with open(project_model_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'document_path = db.Column' not in content:
    content = content.replace("image_path = db.Column(db.String(255))",
                              "image_path = db.Column(db.String(255))\n    document_path = db.Column(db.String(255))")
    with open(project_model_path, 'w', encoding='utf-8') as f:
        f.write(content)

startup_route_path = os.path.join(base_dir, 'routes/startup.py')
with open(startup_route_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'ALLOWED_DOC_EXTENSIONS' not in content:
    content = content.replace("ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}",
                              "ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}\nALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip'}")
    content = content.replace("def allowed_file(filename):\n    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS",
                              "def allowed_file(filename):\n    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS\n\ndef allowed_doc(filename):\n    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS")
    
    replace_block_old = """        file = request.files.get('image')
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{current_user.id}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            image_path = unique_name
            
        new_project = Project(
            owner_id=current_user.id,
            name=name,
            description=description,
            goal_amount=goal_amount,
            category=category,
            duration_days=duration_days,
            image_path=image_path
        )"""
    replace_block_new = """        file = request.files.get('image')
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{current_user.id}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            image_path = unique_name
            
        doc_file = request.files.get('document')
        document_path = None
        if doc_file and allowed_doc(doc_file.filename):
            doc_filename = secure_filename(doc_file.filename)
            doc_unique_name = f"doc_{current_user.id}_{doc_filename}"
            doc_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], doc_unique_name))
            document_path = doc_unique_name
            
        new_project = Project(
            owner_id=current_user.id,
            name=name,
            description=description,
            goal_amount=goal_amount,
            category=category,
            duration_days=duration_days,
            image_path=image_path,
            document_path=document_path
        )"""
    content = content.replace(replace_block_old, replace_block_new)
    with open(startup_route_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 3. Update templates/startup/add_project.html
add_project_html_path = os.path.join(base_dir, 'templates/startup/add_project.html')
with open(add_project_html_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'name="document"' not in content:
    old_html = """                        <div class="col-md-6">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-muted small mb-1 ms-1"><i class="fas fa-image me-1"></i> Cover Image</label>
                                <input type="file" name="image" class="form-control form-control-lg shadow-sm" accept="image/*">
                            </div>
                        </div>"""
    new_html = """                        <div class="col-md-6">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-muted small mb-1 ms-1"><i class="fas fa-image me-1"></i> Cover Image</label>
                                <input type="file" name="image" class="form-control form-control-lg shadow-sm" accept="image/*">
                            </div>
                            <div class="mb-4">
                                <label class="form-label fw-bold text-muted small mb-1 ms-1"><i class="fas fa-file-contract me-1"></i> Legal / Pitch Document</label>
                                <input type="file" name="document" class="form-control form-control-lg shadow-sm" accept=".pdf,.doc,.docx,.txt,.zip">
                                <small class="text-secondary ms-1">PDF, DOC, DOCX, ZIP allowed for Investors</small>
                            </div>
                        </div>"""
    content = content.replace(old_html, new_html)
    with open(add_project_html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 4. Update templates/project_detail.html
project_detail_html_path = os.path.join(base_dir, 'templates/project_detail.html')
with open(project_detail_html_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'Legal Documents' not in content:
    old_html = """                    <div class="col-4">
                        <i class="fas fa-user-tie fa-2x text-info mb-2"></i>
                        <h5 class="fw-bold mb-0">Owner</h5>
                        <p class="text-muted mb-0">{{ project.owner.name }}</p>
                    </div>
                </div>
            </div>"""
    new_html = """                    <div class="col-4">
                        <i class="fas fa-user-tie fa-2x text-info mb-2"></i>
                        <h5 class="fw-bold mb-0">Owner</h5>
                        <p class="text-muted mb-0">{{ project.owner.name }}</p>
                    </div>
                </div>
                
                {% if current_user.is_authenticated and current_user.role == 'investor' %}
                <hr class="text-muted mt-5 mb-4">
                <div class="bg-primary bg-opacity-10 p-4 rounded border border-primary border-opacity-25 shadow-sm">
                    <h4 class="fw-bold text-dark"><i class="fas fa-file-signature text-primary me-2"></i>Legal & Due Diligence</h4>
                    <p class="text-muted mb-4">As an investor evaluating this opportunity, you have secure access to the startup's verified legal files and pitch documents.</p>
                    {% if project.document_path %}
                        <a href="{{ url_for('static', filename='uploads/' ~ project.document_path) }}" class="btn btn-outline-primary fw-bold" target="_blank">
                            <i class="fas fa-file-pdf me-2"></i>View Official Document
                        </a>
                    {% else %}
                        <p class="text-secondary mb-0 fw-bold"><i class="fas fa-info-circle me-1"></i> No legal documents uploaded yet.</p>
                    {% endif %}
                </div>
                {% endif %}
                
            </div>"""
    content = content.replace(old_html, new_html)
    with open(project_detail_html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 5. Update templates/investor/payment.html
payment_html_path = os.path.join(base_dir, 'templates/investor/payment.html')
with open(payment_html_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'NDA' not in content:
    old_html = """                    <button type="submit" class="btn btn-success btn-lg w-100 fw-bold shadow hover-lift py-3"><i class="fas fa-check-circle me-2"></i> Confirm Payment of ${{ '{:,.2f}'.format(investment_amount) }}</button>"""
    new_html = """                    
                    <h5 class="fw-bold text-secondary mb-3 border-bottom pb-2 mt-5"><i class="fas fa-lock text-warning me-2"></i>Non-Disclosure Agreement (NDA)</h5>
                    <div class="bg-white border rounded p-3 mb-3 shadow-inner" style="max-height: 150px; overflow-y: auto;">
                        <p class="text-muted small mb-0">
                            <strong>MUTUAL NON-DISCLOSURE AGREEMENT</strong><br><br>
                            This Non-Disclosure Agreement ("NDA") is entered into by and between the Investor and the Startup Entity linked to this investment on the FundGrow Platform.
                            <br><br>
                            1. <strong>Confidential Information:</strong> In connection with the Investor's consideration of an investment, the Startup may disclose, and may have already disclosed via platform documents, certain trade secrets, financial models, proprietary algorithms, and sensitive intellectual property.
                            <br>2. <strong>Obligations:</strong> The Investor agrees to hold all Confidential Information in strict confidence and not to disclose it to any third party without prior written consent. The Investor also agrees not to use the Confidential Information for any purpose other than evaluating the investment opportunity.
                            <br>3. <strong>Term:</strong> This agreement shall remain in effect for a period of five (5) years from the transaction date.
                            <br><br>By checking the box below and proceeding with this payment, you electronically sign and bind yourself to this Non-Disclosure Agreement.
                        </p>
                    </div>
                    
                    <div class="form-check mb-4 bg-light p-3 border rounded shadow-sm">
                        <input class="form-check-input ms-1 shadow-sm mt-1" type="checkbox" id="ndaAgreement" required>
                        <label class="form-check-label ms-3 text-dark fw-bold" for="ndaAgreement">
                            I accept the NDA and agree to keep project details and documents confidential.
                        </label>
                    </div>

                    <button type="submit" class="btn btn-success btn-lg w-100 fw-bold shadow hover-lift py-3"><i class="fas fa-check-circle me-2"></i> Confirm Payment of ${{ '{:,.2f}'.format(investment_amount) }}</button>"""
    content = content.replace(old_html, new_html)
    with open(payment_html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 6. Make Colors Professional
style_css_path = os.path.join(base_dir, 'static/css/style.css')
with open(style_css_path, 'r', encoding='utf-8') as f:
    content = f.read()
if '--bs-primary: #0f172a;' not in content:
    content += """
/* ----------------------------------
   Professional Fintech Color Palette Overrides
----------------------------------- */
:root {
  --bs-primary: #0f172a;      /* Slate Navy */
  --bs-success: #059669;      /* Emerald Green */
  --bs-info: #0284c7;         /* Ocean Blue */
}

/* Forced Overrides for generic Bootstrap classes to ensure professional layout */
.bg-primary { background-color: #0f172a !important; }
.text-primary { color: #0f172a !important; }
.btn-primary { background-color: #0f172a !important; border-color: #0f172a !important; color: white !important; }
.btn-primary:hover { background-color: #1e293b !important; border-color: #1e293b !important; }
.btn-outline-primary { color: #0f172a !important; border-color: #0f172a !important; }
.btn-outline-primary:hover { background-color: #0f172a !important; color: white !important; }

.bg-success { background-color: #059669 !important; }
.text-success { color: #059669 !important; }
.btn-success { background-color: #059669 !important; border-color: #059669 !important; color: white !important; }
.btn-success:hover { background-color: #047857 !important; border-color: #047857 !important; }
.btn-outline-success { color: #059669 !important; border-color: #059669 !important; }
.btn-outline-success:hover { background-color: #059669 !important; color: white !important; }

.bg-info { background-color: #0284c7 !important; }

/* Global Gradients */
.navbar, .banner, .card-header.bg-primary {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}
.card-header.bg-success {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
}
.text-primary-light { color: #cbd5e1 !important; }
"""
    with open(style_css_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 7. Migrate Database and Seed Real Projects
def migrate_db():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='', database='fundgrow')
        cursor = connection.cursor()

        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN document_path VARCHAR(255);")
            connection.commit()
            print("Added document_path column to DB.")
        except Exception as e:
            print("Column 'document_path' might already exist or error:", e)

        # Ensure we have a sample startup user
        cursor.execute("SELECT id FROM users WHERE email='startup@fundgrow.com'")
        user = cursor.fetchone()
        if not user:
            from werkzeug.security import generate_password_hash
            pw = generate_password_hash('Startup@123')
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Innovate Labs', 'startup@fundgrow.com', %s, 'startup')", (pw,))
            connection.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user[0]

        # Ensure we have a sample investor user
        cursor.execute("SELECT id FROM users WHERE email='investor@fundgrow.com'")
        inv = cursor.fetchone()
        if not inv:
            from werkzeug.security import generate_password_hash
            pw = generate_password_hash('Investor@123')
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Elite Investor', 'investor@fundgrow.com', %s, 'investor')", (pw,))
            connection.commit()

        cursor.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] == 0:
            # Create a mock document file in uploads to avoid broken links
            uploads_dir = os.path.join(base_dir, 'static/uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            mock_doc_name = 'pitch_deck_innovate_labs.txt'
            with open(os.path.join(uploads_dir, mock_doc_name), 'w') as f:
                f.write("CONFIDENTIAL PITCH DECK & FINANCIAL PROJECTIONS\n\nThis is a mock legal/pitch document for demonstration.")
                
            cursor.execute("""
                INSERT INTO projects (owner_id, name, description, goal_amount, raised_amount, category, duration_days, status, image_path, document_path)
                VALUES 
                (%s, 'EcoCharge EV Network', 'Building a nationwide network of fast, renewable-powered EV charging stations. Targeting urban centers with high EV adoption rates and expanding to rural travel corridors. We aim to install 500 stations within 24 months, tapping into a $15B market.', 750000.00, 250000.00, 'Environment', 60, 'approved', NULL, %s),
                (%s, 'HealthAI Diagnostics', 'AI-powered diagnostic tool for early detection of rare diseases through automated blood work analysis and pattern recognition. Certified by ISO, we are moving to clinical trials targeting top-tier US hospitals.', 1500000.00, 450000.00, 'Health', 45, 'approved', NULL, %s),
                (%s, 'FinSecure Gateway', 'Next-generation payment gateway with quantum-resistant encryption and real-time fraud prevention utilizing machine learning. Projected API integrations with major e-commerce platforms in Q4 2026.', 2000000.00, 150000.00, 'Finance', 90, 'approved', NULL, NULL),
                (%s, 'EduVirtual Reality', 'Immersive VR classrooms bringing ivy-league level science labs to students worldwide. Partnered with 50 school districts for pilot programs.', 500000.00, 50000.00, 'Education', 30, 'approved', NULL, NULL)
            """, (user_id, mock_doc_name, user_id, mock_doc_name, user_id, user_id))
            connection.commit()
            print("Inserted sample professional projects.")

        connection.close()
    except Exception as e:
        print("Database error:", e)

migrate_db()
print("All patches applied successfully!")
