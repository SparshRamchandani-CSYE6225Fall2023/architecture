from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda, AutoScaling
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.network import Route53, ELB, VPC, PrivateSubnet, PublicSubnet, InternetGateway, NATGateway
from diagrams.aws.security import IAM, CertificateManager
from diagrams.aws.storage import S3
from diagrams.aws.integration import SNS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import Users
from diagrams.gcp.storage import GCS
from diagrams.programming.language import NodeJS
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.vcs import Github
from diagrams.custom import Custom

with Diagram("CSYE6225 Cloud Architecture with CI/CD", show=False, filename="cloud_architecture_diagram"):
    users = Users("Users")

    with Cluster("GitHub"):
        github = Github("Repository")
        with Cluster("GitHub Actions"):
            build_ci = GithubActions("Build CI")
            build_ami = GithubActions("Build AMI")
            packer_check = Custom("Packer Check", "./my_resources/packer.svg")

    pulumi = Custom("IaC", "./my_resources/pulumiio-ar21.svg")

    with Cluster("AWS Cloud"):
        route53 = Route53("Route53")
        
        with Cluster("VPC"):
            vpc = VPC("Custom VPC")

            with Cluster("Public Subnets"):
                public_subnets = [PublicSubnet("Public Subnet 1"),
                                  PublicSubnet("Public Subnet 2"),
                                  PublicSubnet("Public Subnet 3")]

            with Cluster("Private Subnets"):
                private_subnets = [PrivateSubnet("Private Subnet 1"),
                                   PrivateSubnet("Private Subnet 2"),
                                   PrivateSubnet("Private Subnet 3")]

            igw = InternetGateway("Internet Gateway")
            nat = NATGateway("NAT Gateway")

            elb = ELB("Application Load Balancer")
            
            with Cluster("Auto Scaling Group"):
                asg = AutoScaling("Auto Scaling")
                ec2_instances = [EC2("EC2 Instance 1"),
                                 EC2("EC2 Instance 2"),
                                 EC2("EC2 Instance 3")]

            rds = RDS("RDS PostgreSQL")
            s3 = S3("S3 Bucket")
            cloudwatch = Cloudwatch("Cloudwatch")
            iam = IAM("IAM")
            sns = SNS("SNS Topic")
            acm = CertificateManager("ACM SSL Certificate")

        lambda_function = Lambda("Lambda Function")
        dynamodb = Dynamodb("Dynamodb")

    with Cluster("Google Cloud Platform"):
        gcs = GCS("Google Cloud Storage")

    # Pulumi Connection
    pulumi >> Edge(label="Provision Infrastructure") >> vpc

    # CI/CD Connections
    github >> build_ci
    github >> build_ami
    github >> packer_check
    build_ami >> Edge(label="Create AMI") >> asg
    build_ami >> Edge(label="Update Launch Template") >> asg
    build_ami >> Edge(label="Start Instance Refresh") >> asg

    # Other Connections
    users >> route53
    route53 >> elb
    elb >> Edge(label="HTTPS") >> asg
    asg - ec2_instances
    ec2_instances >> Edge(label="Read/Write") >> rds
    ec2_instances >> Edge(label="Store/Retrieve") >> s3
    ec2_instances >> Edge(label="Log") >> cloudwatch
    ec2_instances >> Edge(label="Authenticate") >> iam
    ec2_instances >> sns

    sns >> lambda_function
    lambda_function >> dynamodb
    lambda_function >> gcs
    lambda_function >> Edge(label="Send Email") >> Users("Email Recipients")

    # VPC connections
    igw >> public_subnets
    public_subnets >> nat
    nat >> private_subnets
    private_subnets >> rds

    # Security
    acm - elb

    # Application
    with Cluster("EC2 Instance"):
        app = NodeJS("Node.js App")
        express = Custom("Express.js", "./my_resources/expressjs-icon.svg")
        
        with Cluster("API Routes"):
            postman_icon = Custom("", "./my_resources/postman.svg")
            get_all = Custom("GET /", "./my_resources/postman.svg")
            get_by_id = Custom("GET /:id", "./my_resources/postman.svg")
            post = Custom("POST /", "./my_resources/postman.svg")
            post_submission = Custom("POST /:id/submissions", "./my_resources/postman.svg")
            delete = Custom("DELETE /:id", "./my_resources/postman.svg")
            put = Custom("PUT /:id", "./my_resources/postman.svg")

        app >> express
        express >> postman_icon - [get_all, get_by_id, post, post_submission, delete, put]

        app >> Edge(label="Connect") >> rds
        app >> Edge(label="Use") >> s3
        app >> Edge(label="Publish") >> sns
