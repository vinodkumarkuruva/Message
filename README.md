-->Installation and Setup
     
1) Prerequisites - 

	     Python 3.7+: Ensure that Python is installed on your system
	     Flask - As a Framework - Backend
         Bootstrap - For Frontend
		
   
2) Steps to Set Up -

		  Create a virtual environment          :    python3 -m venv < name of virtual Environment > 
			
		  To activate the virtual Environment   :    < name of virtual Environment >/Scripts/activate 
		
		  Install dependencies                  :    pip install -r requirements.txt
		
		  Set up the database                   :    flask db init
			                                         flask db migrate -m "Initial migration"
													 flask db upgrade
		
		  Run the server                        :    Python run.py (or) flask run
		
		  * The application will start and be accessible at http://127.0.0.1:5000

		




