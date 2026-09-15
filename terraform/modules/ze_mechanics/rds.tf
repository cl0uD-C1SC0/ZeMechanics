# AWS RDS Configs

resource "aws_db_subnet_group" "subnetgroup" {
  name       = "zemechcanicssubnetgroup"
  subnet_ids = [aws_subnet.us-east-1a-priv.id, aws_subnet.us-east-1b-priv.id ]

  tags = {
    Name = "My DB subnet group"
  }
}

resource "aws_db_instance" "zemechanics-rds" {
  allocated_storage    = 20
  db_name              = "mecanica"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  username             = "admin"
  password             = "rootroot"
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true

  db_subnet_group_name = "zemechcanicssubnetgroup"
  vpc_security_group_ids = [ aws_security_group.rds-sg.id ]
  
  depends_on = [ aws_db_subnet_group.subnetgroup ]
}

# Configurar connection da funcao lambda auth-issuer para o RDS
