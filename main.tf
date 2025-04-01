provider "aws" {}
resource "aws_vpc" "tf_vpc1"{
  cidr_block = "10.0.0.0/16"
  tags ={
    name = "tf_vpc1"
  }
}
resource "aws_subnet" "tf_sub-1"{
  vpc_id = aws_vpc.tf_vpc1.id
  availability_zone = "us-east-1a"
  cidr_block = "10.0.1.0/24"
  tags ={
    name = "tf_sub-1"
  }
}
resource "aws_subnet" "tf_sub-2"{
  vpc_id = aws_vpc.tf_vpc1.id
  availability_zone = "us-east-1b"
  cidr_block = "10.0.2.0/24"
  tags ={
    name = "tf_sub-2"
  }
}
resource "aws_route_table" "tf_route1"{
  vpc_id = aws_vpc.tf_vpc1.id
  route{
    cidr_block ="0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw1.id
  }
  tags ={
    name ="tf_route1"
  }

}
resource "aws_route_table" "tf_route2"{
  vpc_id = aws_vpc.tf_vpc1.id
  route= []
  tags ={
    name ="tf_route2"
  }

}
resource "aws_route_table_association" "a"{
  subnet_id =aws_subnet.tf_sub-2.id
  route_table_id = aws_route_table.tf_route2.id
}
resource "aws_internet_gateway" "igw1"{
  tags ={
    name = "igw1"
  }
}
resource "aws_internet_gateway_attachment" "igw_attachment"{
  internet_gateway_id = aws_internet_gateway.igw1.id
  vpc_id              = aws_vpc.tf_vpc1.id
}
resource "aws_route_table_association" "tf_sub_association"{
  subnet_id = aws_subnet.tf_sub-1.id
  route_table_id = aws_route_table.tf_route1.id
}
resource "aws_security_group" "tf_sg1"{
  vpc_id= aws_vpc.tf_vpc1.id

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress{
    from_port = 80
    to_port   = 80
    protocol  ="tcp"
    cidr_blocks =["0.0.0.0/0"]
  }
  egress{
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks =["::/0"]
  }
  tags = {
    name= "tf_sg1"
      }
}
resource "aws_key_pair" "tf_keys"{
  key_name = "tf_keys"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCzjX8fSdjOPA3ot/JnX+TMieItWHlphHy3ZFx6keGonQdsqgLoirSXpW9fNCnUj1qBK/J/nh2uNZIzHpl+w3wEnj81LrrSY3xqtab7QPrtOBl+mI9sMH9Nm2dAUwYjdD5eS6Y7rhvjtPTcKujfYsHufXynCCCvBwyiDSPM/EYYKUMwuWCM37dwH+gPIBJjNrqQIXSIeQtu4Tdg3H4XrJv44qPtGzdnOmpjH4iG68priwOBo4XMb/7CZjkrvH7RzRekYJEJOWoMeYUhMOS8rcKepqfjuoPjFnOwg0Ogk8U/POfDXfPzIbHHYjUPgA6px1CElsnwYgD6ST3ePZdrBs6rk7Am1eh3UfMTeWKNEFfzf7hMiESYpcMIbEM0yBDU5mtn1R3QhG02JpjbxwyPtNkaXH0tcDFcrxcizzgsSuc7uSunYGAazN9h/xEo03SOujVqi7w3U91vdttDZ2KB4Cm/8tWeUTeXq3TOoXC7FU/wWkFWUyZbMFgAHukkQ3DyBG0= sarav@kanishka"
}
resource "aws_instance" "server-1"{
  ami = data.aws_ami.centOs1.id
  instance_type = "t2.micro"
  key_name = aws_key_pair.tf_keys.key_name
  subnet_id= aws_subnet.tf_sub-1.id
  security_groups =[aws_security_group.tf_sg1.id]
  availability_zone = "us-east-1a"
  tags ={
    name ="server-1"
  }
}
data "aws_ami""centOs1"{
  most_recent = true 
  owners      = ["amazon"]

  filter{
    name ="name"
    values=["RHEL-9.4.0_HVM-20240605-x86_64-82-Hourly2-GP3"]
  }
  filter{
    name = "virtualization-type"
    values = ["hvm"]
  }
}
