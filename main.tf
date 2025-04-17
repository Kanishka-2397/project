provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "tf_vpc1" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "tf_vpc1"
  }
}

# Subnet 1
resource "aws_subnet" "tf_sub-1" {
  vpc_id            = aws_vpc.tf_vpc1.id
  availability_zone = "us-east-1a"
  cidr_block        = "10.0.1.0/24"
  tags = {
    Name = "tf_sub-1"
  }
}

# Subnet 2
resource "aws_subnet" "tf_sub-2" {
  vpc_id            = aws_vpc.tf_vpc1.id
  availability_zone = "us-east-1b"
  cidr_block        = "10.0.4.0/24"
  tags = {
    Name = "tf_sub-2"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw1" {
  tags = {
    Name = "igw1"
  }
}

# Attach IGW to VPC
resource "aws_internet_gateway_attachment" "igw_attachment" {
  internet_gateway_id = aws_internet_gateway.igw1.id
  vpc_id              = aws_vpc.tf_vpc1.id
}

# Route Table 1 (Public)
resource "aws_route_table" "tf-rt1" {
  vpc_id = aws_vpc.tf_vpc1.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw1.id
  }

  tags = {
    Name = "tf-rt1"
  }
}

# Route Table 2 (Private)
resource "aws_route_table" "tf-rt2" {
  vpc_id = aws_vpc.tf_vpc1.id
  route  = []
  tags = {
    Name = "tf-rt2"
  }
}

# Associate subnet-1 with public route table
resource "aws_route_table_association" "demo_sub_1_association" {
  subnet_id      = aws_subnet.tf_sub-1.id
  route_table_id = aws_route_table.tf-rt1.id
}

# Associate subnet-2 with private route table
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.tf_sub-2.id
  route_table_id = aws_route_table.tf-rt2.id
}

# Security Group
resource "aws_security_group" "terra_sg1" {
  vpc_id = aws_vpc.tf_vpc1.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 50000
    to_port     = 50000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    cidr_blocks       = ["0.0.0.0/0"]
    ipv6_cidr_blocks  = ["::/0"]
  }

  tags = {
    Name = "Terraform_SG"
  }
}

# EC2 Instances (Ubuntu)
resource "aws_instance" "my_ec2_instance" {
  count             = 2
  ami               = "ami-084568db4383264d4" # Ubuntu 22.04 LTS in us-east-2
  instance_type     = "t2.micro"
  key_name          = "TFF" # Replace with your actual key name
  subnet_id         = aws_subnet.tf_sub-1.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.terra_sg1.id]

  tags = {
    Name = "Ubuntu Server-${count.index + 1}"
  }
}

# Outputs
output "instance_public_ip" {
  value = aws_instance.my_ec2_instance[*].public_ip
}

output "instance_id" {
  value = aws_instance.my_ec2_instance[*].id
}

