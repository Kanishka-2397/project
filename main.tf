provider "aws" {}

resource "aws_vpc" "vpc1" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "vpc1"
  }
}

resource "aws_subnet" "sub1" {
  availability_zone = "us-east-1a"
  cidr_block        = "10.0.0.0/23"
  vpc_id            = aws_vpc.vpc1.id

  tags = {
    Name = "aws_subnet1"
  }
}

resource "aws_subnet" "sub2" {
  availability_zone = "us-east-1c"
  cidr_block        = "10.0.2.0/23"
  vpc_id            = aws_vpc.vpc1.id

  tags = {
    Name = "aws_subnet2"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc1.id
}

resource "aws_route_table" "route" {
  vpc_id = aws_vpc.vpc1.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "route"
  }
}

resource "aws_route_table_association" "sub1_assoc" {
  subnet_id      = aws_subnet.sub1.id
  route_table_id = aws_route_table.route.id
}

