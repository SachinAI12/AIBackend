# Use the official Python 3.8.10 image as a base
FROM python:3.8.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install MySQL development dependencies 
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential && apt-get clean




# Copy the requirements file and install dependencies
COPY requirements.txt /app/




#ensure the latest CA certificates are available for SSL verification
# RUN apt-get update && apt-get install -y ca-certificates
# RUN update-ca-certificates

# Upgrade pip to the latest version
#RUN python -m pip install --upgrade pip

# to disable the SSL verification in pip if we trust the source not recommended in prod 
#use this in general: 
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org -r requirements.txt



# Copy the Django project files into the container
COPY . /app/

# Expose the port that Django will run on
EXPOSE 3000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
