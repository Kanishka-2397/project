FROM python:latest
RUN apt update 
RUN pip install boto3
RUN pip install requests
WORKDIR /var/myapp
COPY aws.py /var/myapp/aws.py
CMD ["sh", "-c", "python /var/myapp/aws.py"]
