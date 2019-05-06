from troposphere import Base64, FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Template
import troposphere.ec2 as ec2


template = Template()

template.add_parameter(Parameter(
    "KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH "
                "access to the instance",
    Type="AWS::EC2::KeyPair::KeyName",
))

template.add_parameter(Parameter(
    "InstanceType",
    Description="EC2 instance type",
    Type="String",
    Default="t2.micro",
    AllowedValues=[
        "t2.micro"
    ],
    ConstraintDescription="Must be a valid EC2 instance type."
))

template.add_parameter(Parameter(
    "CIDRLocation",
    Description="Public IP address of the location accessing the instance.",
    Type="String",
    Default="205.118.217.10/32",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    ConstraintDescription="Must be a valid CIDR (x.x.x.x/x)"
))

template.add_resource(ec2.SecurityGroup(
    "InstanceSG",
    GroupDescription="Default SG for the CF instance.",
    GroupName=Join("", [
        Ref("AWS::StackName"),
        "-sg"
    ]),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            "",
            CidrIp=Ref("CIDRLocation"),
            FromPort="22",
            ToPort="22",
            IpProtocol="tcp",
        ),
        ec2.SecurityGroupRule(
            "",
            CidrIp=Ref("CIDRLocation"),
            FromPort="80",
            ToPort="80",
            IpProtocol="tcp",
        ),
        ec2.SecurityGroupRule(
            "",
            CidrIp=Ref("CIDRLocation"),
            FromPort="443",
            ToPort="443",
            IpProtocol="tcp",
        )
    ],
    VpcId="vpc-eaadff93"
))

template.add_resource(ec2.Instance(
    "Ec2Instance",
    ImageId="ami-061392db613a6357b",
    InstanceType=Ref("InstanceType"),
    KeyName=Ref("KeyName"),
    SecurityGroupIds=[
        GetAtt("InstanceSG", "GroupId")
    ],
    SubnetId="subnet-0fdeea37a83c66cc7",
    UserData=Base64(
        Join(
            "",
            [
                "sudo yum update -y \n",
                "sudo amazon-linux-extras install docker -y \n",
                "sudo systemctl enable docker \n",
                "sudo systemctl start docker \n",
                "sudo usermod -aG ec2-user docker \n",
                "sudo docker pull ghost:latest \n",
                "sudo docker run -d ",
                "    --name ghost ",
                "    -p 443:2368 ",
                "    ghost:latest \n"
            ]
        )
    )
))

template.add_output([
    Output(
        "InstanceId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref("Ec2Instance"),
    ),
    Output(
        "PublicIP",
        Description="Public IP address of the newly created EC2 instance",
        Value=GetAtt("Ec2Instance", "PublicIp"),
    ),
    Output(
        "PublicDNS",
        Description="Public DNSName of the newly created EC2 instance",
        Value=GetAtt("Ec2Instance", "PublicDnsName"),
    ),
])

print(template.to_json())
