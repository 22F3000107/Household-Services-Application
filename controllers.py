from flask import  flash,render_template,request,redirect,session,url_for,send_from_directory
from app import app
from models import db, User,Customer,Service,ServiceRequest,ServiceProfessional
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
import os
from flask import request



# Utility function to validate file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc','docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/') # this is base url 127.0.0.1:5000
def index():
  flash ("This is index page!")
  return render_template('index.html')
@app.route('/login',methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        email=request.form.get('email')
        password= request.form.get('password')

        this_user = User.query.filter_by(email=email).first()
     
        if this_user and check_password_hash(this_user.password, password):
            
           session['user_id'] = this_user.id
           session['username'] = this_user.username
           session['role'] = this_user.role  # Admin, Customer

           flash('Login successful!', 'success')
        
           if this_user.role == 'Customer':
                customer = Customer.query.filter_by(id=this_user.id).first()
                if customer:
                    session['customer_id'] = customer.id
                else:
                    flash('Error: No associated customer record found!', 'danger')
                    return redirect(url_for('user_login'))
                return redirect(url_for('customer_dashboard'))
           
           elif this_user.role == 'Admin':
                
                session['admin_id'] = this_user.id
                return redirect(url_for('admin_dashboard'))


        else:
            flash('Invalid email or password!', 'danger')

    return render_template('userlogin.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email= request.form.get('email')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        contact=request.form.get('contact')

        if not username or not email or not password or not confirm_password  or not address or not pincode:
            flash('All fields are required.', 'error')
            return redirect('/register')
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect('/register')

        this_user = User.query.filter_by(email=email).first()
        if this_user:
            flash('Email already registered.', 'error')
            return redirect('/register')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username,email=email,password=hashed_password,role='Customer')
        db.session.add(new_user)
        db.session.commit()

    
        new_customer = Customer(name=username,address=address,pincode=pincode,contact=contact,user=new_user)
        db.session.add(new_customer)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect('/login') 

    
    return render_template('register.html')

@app.route('/professional_login',methods=['GET','POST'])
def professional_login():
  if request.method == 'POST':
     email=request.form.get('email')
     password= request.form.get('password')
     if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('professional_login.html')

     this_user = User.query.filter_by(email=email).first()
     if not this_user:
            flash('User with this email does not exist.', 'error')
            return render_template('professional_login.html')

     if not check_password_hash(this_user.password, password):
            flash('Incorrect password. Please try again.', 'error')
            return render_template('professional_login.html') 
      
     professional = ServiceProfessional.query.filter_by(id=this_user.id).first()
     if not professional:
            flash('This account is not registered as a Service Professional.', 'error')
            return render_template('professional_login.html') 
     
     session['user_id'] = this_user.id
     session['username'] = this_user.username
     session['role'] = 'Serviceprofessional'  #  Service Professional 
     session['professional_id'] = professional.id

     flash('Login successful!', 'success')
     return redirect(url_for('professional_dashboard'))
  
  return render_template('professional_login.html')


@app.route('/professional_register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        phone = request.form.get('phone')
        file = request.files.get('documents')

        # Validate mandatory fields
        if not email or not password or not name:
            flash('Email, password, and name are required.', 'error')
            return redirect(url_for('professional_register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('professional_register'))

        # Check if email is already registered
        this_user = User.query.filter_by(email=email).first()
        if this_user:
            flash('Email is already registered!', 'error')
            return redirect(url_for('professional_register'))

        # Process document upload
        filename = None  # Default value for filename
        if file and allowed_file(file.filename):
            # Secure filename and save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            flash('Invalid document file. Please upload a valid file.', 'error')
            return redirect(url_for('professional_register'))

        # Create new user
        new_user = User(
            username=email,
            email=email,
            password=generate_password_hash(password),
            role='ServiceProfessional'
        )
        db.session.add(new_user)
        db.session.commit()

        # Create new professional profile
        new_professional = ServiceProfessional(
            name=name,
            service_type=service_type,
            experience=experience,
            address=address,
            pincode=pincode,
            phone=phone,
            documents=filename,  # Assign the filename for the uploaded document
            profile_verified=False,
            user=new_user
        )
        db.session.add(new_professional)
        db.session.commit()

        flash('Professional account created successfully! Please log in.', 'success')
        return redirect('/professional_login')
    services = Service.query.all()
    return render_template('professional_register.html',services = services)

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    if 'user_id' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get(user_id)
        customer = user.customer
        services = Service.query.all()
        service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
        professionals = ServiceProfessional.query.all()
        return render_template('customer_dashboard.html', customer=customer, services=services, service_requests=service_requests,professionals=professionals)
    else:
        flash('Please log in to access your dashboard', 'error')
        return redirect(url_for('user_login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('user_login'))
@app.route('/professional_logout')
def professional_logout():
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('professional_login'))

# customer dashboard
@app.route('/customer/request_service/<int:service_id>', methods=['GET', 'POST'])
def request_service(service_id):
    service = Service.query.get_or_404(service_id)

    # Fetch service professionals who match the service type
    professionals = ServiceProfessional.query.filter_by(service_type=service.name, profile_verified=True).all()

    if request.method == 'POST':
        customer_id = session['customer_id']  
        professional_id = int(request.form.get('professional_id')) 
        

        # Create and save the service request
        service_request = ServiceRequest(
            service_id=service_id,
            customer_id=customer_id,
            professional_id=professional_id,
            date_of_request=datetime.now(),
            status='Requested'
        )
        db.session.add(service_request)
        db.session.commit()

        flash('Service request created successfully!', 'success')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('request_service.html', service=service, professionals=professionals)

@app.route('/customer/request_service_with_filters/<int:service_id>',methods=['GET'])
def request_service_with_filters(service_id):
    service = Service.query.get_or_404(service_id)
    address_filter = request.args.get('address')
    experience_filter = request.args.get('experience')

    # Apply filters to professionals
    query = ServiceProfessional.query.filter_by(service_type=service.name, profile_verified=True)
    if address_filter:
        query = query.filter(ServiceProfessional.address.contains(address_filter))
    if experience_filter:
        query = query.filter(ServiceProfessional.experience >= int(experience_filter))

    professionals =ServiceProfessional.query.all()
    return render_template('request_service.html', service=service, professionals=professionals)

@app.route('/customer/edit_request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def edit_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if request.method == 'POST':
        service_request.status = request.form.get('status')
        service_request.date_of_completion = request.form.get('date_of_completion')
        db.session.commit()
        flash('Service Request Updated Successfully!', 'success')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('edit_service_request.html', request=service_request)


@app.route('/close_service_requests/<int:request_id>', methods=['POST'])
def close_service_requests(request_id):
    # Check if the user is logged in as a customer
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You must be logged in as a customer to close a service request.', 'error')
        return redirect(url_for('customer_login'))

    # Fetch the service request by ID
    service_request = ServiceRequest.query.filter_by(id=request_id, customer_id=customer_id).first()

    if not service_request:
        flash('Service request not found or you do not have permission to close it.', 'error')
        return redirect(url_for('customer_dashboard'))

    # Check if the service request is in a valid status for closing
    if service_request.status != 'Assigned':
        flash('Only Assigned services can be closed.', 'error')
        return redirect(url_for('customer_dashboard'))

    # Update the status of the service request to 'Closed'
    service_request.status = 'Closed'
    service_request.date_of_completion = datetime.now()  # Set the completion date
    db.session.commit()

    # Redirect to a page where the customer can rate the service and leave remarks
    flash('Service successfully closed. Please provide a rating and remarks.', 'success')
    return redirect(url_for('rate_service', request_id=service_request.id))
@app.route('/rate_service/<int:request_id>', methods=['GET', 'POST'])
def rate_service(request_id):
    # Check if the user is logged in as a customer
    customer_id = session.get('customer_id')
    if not customer_id:
        flash('You must be logged in as a customer to rate a service.', 'error')
        return redirect(url_for('customer_login'))

    # Fetch the service request
    service_request = ServiceRequest.query.filter_by(id=request_id, customer_id=customer_id).first()

    if not service_request or service_request.status != 'Closed':
        flash('Invalid service request or the service is not yet closed.', 'error')
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        remarks = request.form.get('remarks')

        # Validate input
        if not rating or int(rating) < 1 or int(rating) > 5:
            flash('Please provide a valid rating between 1 and 5.', 'error')
            return redirect(url_for('rate_service', request_id=request_id))

        # Update the service request with rating and remarks
        service_request.remarks = remarks
        service_request.rating = int(rating)  # Assuming rating is added in the model
        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('rate_service.html', service_request=service_request)

# admin dashboard
@app.route('/documents/<filename>')
def get_document(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "File not found", 404



@app.route('/admin_dashboard',methods=['GET'])
@login_required
def admin_dashboard():
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    professionals =ServiceProfessional.query.all()
    pending_professionals = ServiceProfessional.query.filter_by(profile_verified=False, rejected=False).all()
    return render_template('admin_dashboard.html',services=services,service_requests=service_requests,professionals=professionals,pending_professionals=pending_professionals)


@app.route('/admin/create_service', methods=['GET', 'POST'])
def create_service():
    if request.method == 'POST':
        # Get form data
        service_name = request.form.get('service_name')
        base_price = request.form.get('base_price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')

        if not service_name or not description:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('create_service'))

        # Add new service to the database
        new_service = Service(name=service_name,  base_price=base_price, time_required=time_required,description=description)
        db.session.add(new_service)
        db.session.commit()

        flash('Service created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_service.html') 

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        service.name = request.form['name']
        service.base_price = request.form['base_price']
        service.time_required = request.form['time_required']
        service.description = request.form['description']

        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('edit_service.html', service=service)

@app.route('/services/delete/<int:id>')
def delete_service(id):
    service = Service.query.get(id)
    db.session.delete(service)
    db.session.commit()
    return redirect('/admin_dashboard')
# appprove professional route
@app.route('/professionals/approve/<int:professional_id>',methods=['GET'])
@login_required
def approve_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    professional.profile_verified = True
    db.session.commit()

    flash(f"{professional.name} approved successfully!","success")
    return redirect(url_for('admin_dashboard'))
# reject professional
@app.route('/professionals/reject/<int:professional_id>',methods=['GET'])
@login_required
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    professional.rejected = True
    db.session.commit()

    
    flash(f"Professional {professional.name} rejected successfully.")
    return redirect(url_for('admin_dashboard'))


@app.route('/service_requests/assign/<int:request_id>', methods=['POST', 'GET'])
def assign_professional(request_id):
    professional_id = request.form.get('professional_id')

    if not professional_id:
        flash("Please select a professional to assign.", "error")
        return redirect('/admin_dashboard') 
    
    service_request = ServiceRequest.query.get(request_id)
    professional = ServiceProfessional.query.get(professional_id)
    
    if service_request and professional:
        service_request.professional_id = professional.id
        service_request.status = "Assigned"
        db.session.commit()
        flash("Service request assigned successfully!")
    else:
        flash ("Invalid service request or professional.")
    return redirect('/admin_dashboard') 
@app.route('/service_requests/close/<int:request_id>', methods=['POST', 'GET'])
def close_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if service_request:
        service_request.status = "Closed"
        service_request.date_of_completion = datetime.now()  # Record the completion date
        db.session.commit()
    return redirect('/admin/dashboard')
@app.route('/service_requests/delete/<int:request_id>', methods=['POST', 'GET'])
def delete_service_requests(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if service_request:
        db.session.delete(service_request)
        db.session.commit()
    return redirect('/admin_dashboard') 



# professional dashboard
@app.route('/professional_dashboard')
def professional_dashboard():
    professional_id = session.get('professional_id')
    if not professional_id:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('professional_login'))
    
    print(f"Logged-in Professional ID: {professional_id}")

    # Pending requests
    pending_requests = ServiceRequest.query.filter_by(professional_id=professional_id, status='Requested').all()
    print(f"Pending Requests: {len(pending_requests)}")

    # Accepted and Closed
    accepted_requests = ServiceRequest.query.filter_by(professional_id=professional_id, status='Assigned').all()
    closed_requests = ServiceRequest.query.filter_by(professional_id=professional_id, status='Closed').all()

    return render_template(
        'professional_dashboard.html',
        pending_requests=pending_requests,
        accepted_requests=accepted_requests,
        closed_requests=closed_requests,
    )

  
@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Update the status to 'Assigned'
    service_request.status = 'Assigned'
    db.session.commit()

    flash('Request accepted successfully!', 'success')
    return redirect(url_for('professional_dashboard')) 
# reject request
@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Update the status or remove the request as per your logic
    db.session.delete(service_request)
    db.session.commit()

    flash('Request rejected successfully!', 'success')
    return redirect(url_for('professional_dashboard'))

@app.route('/close_request/<int:request_id>', methods=['POST'])
def close_request(request_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Update the status to 'Closed'
    service_request.status = 'Closed'
    service_request.date_of_completion = datetime.now()
    db.session.commit()

    flash('Request closed successfully!', 'success')
    return redirect(url_for('professional_dashboard'))


# search services  route for customer 
@app.route('/search_services', methods=['GET', 'POST'])
def search_service():
    query = None
    results = []
    customer_id = session.get('user_id') 

    if not customer_id:
        flash('You must be logged in as a customer to search for services.', 'error')
        return redirect(url_for('customer_login'))  

   
    customer = Customer.query.filter_by(id=customer_id).first()
    
    if request.method == 'POST':
        query = request.form.get('query')  
        search_by = request.form.get('search_by')  

        # Search logic
        if search_by == 'service_name':
            results = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
        elif search_by == 'location':
            results = ServiceProfessional.query.filter(ServiceProfessional.address.ilike(f'%{query}%')).all()
        elif search_by == 'pincode':
            results = ServiceProfessional.query.filter(ServiceProfessional.pincode == query).all() 
        elif search_by == 'professional_name':
            results = ServiceProfessional.query.filter(ServiceProfessional.name.ilike(f'%{query}%')).all()
        
    
    return render_template('customer_search_services.html', query=query, results=results,customer=customer)

# Admin search for professionals 
@app.route('/admin_search_professionals', methods=['GET', 'POST'])
def admin_search_professionals():
    if 'admin_id' not in session:  
        flash('You must be logged in as an admin to access this feature.', 'error')
        return redirect(url_for('user_login'))

    query = None
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        search_by = request.form.get('search_by')

        # Search logic
        if search_by == 'name':
            results = ServiceProfessional.query.filter(ServiceProfessional.name.ilike(f'%{query}%')).all()
        elif search_by == 'location':
            results = ServiceProfessional.query.filter(ServiceProfessional.address.ilike(f'%{query}%')).all()
        elif search_by == 'pincode':
            results = ServiceProfessional.query.filter(ServiceProfessional.pincode == query).all()
    
    return render_template('admin_search_professionals.html', query=query, results=results)
 

#  routes for admin to professional for search 
@app.route('/block_unblock_professional/<int:professional_id>', methods=['POST'])
def block_unblock_professional(professional_id):
    if 'admin_id' not in session:  # Check admin login
        flash('You must be logged in as an admin to access this feature.', 'error')
        return redirect(url_for('user_login'))

    action = request.form.get('action')
    professional = ServiceProfessional.query.get_or_404(professional_id)

    if action == 'block':
        professional.status = 'Blocked'
        flash(f'{professional.name} has been blocked.', 'success')
    elif action == 'unblock':
        professional.status = 'Active'
        flash(f'{professional.name} has been unblocked.', 'success')

    db.session.commit()
    return redirect(url_for('admin_search_professionals')) 
@app.route('/admin_review_professional/<int:professional_id>', methods=['GET', 'POST'])
def admin_review_professional(professional_id):
    if 'admin_id' not in session:  # Check admin login
        flash('You must be logged in as an admin to access this feature.', 'error')
        return redirect(url_for('user_login'))

    professional = ServiceProfessional.query.get_or_404(professional_id)

    if request.method == 'POST':
        review = request.form.get('review')
        professional.review = review
        db.session.commit()
        flash(f'Review added for {professional.name}.', 'success')
        return redirect(url_for('admin_search_professionals'))

    return render_template('admin_review_professional.html', professional=professional) 
# @app.route('/view_professional_details/<int:professional_id>', methods=['GET'])
# def view_professional_details(professional_id):
#     if 'admin_id' not in session:
#         flash('You must be logged in as an admin to access this feature.', 'error')
#         return redirect(url_for('login'))

#     professional = ServiceProfessional.query.get_or_404(professional_id)
#     return render_template('view_professional_details.html', professional=professional)  
