#!/usr/bin/env python

import os
import sys

import click


@click.command()
@click.help_option('--help', '-h')
@click.option('--stack-name', default='aws-moodle', help='Cloudformation stack name. Must be unique', show_default=True)
@click.option('--region', default='eu-west-1', help='ec2 region', show_default=True)
@click.option('--ami', default='ami-6e28b517', help='ec2 ami', show_default=True)
@click.option('--bastion-instance-type', default='t2.micro', help='ec2 instance type', show_default=True)
@click.option('--keypair', help='ec2 keypair name', show_default=True)
@click.option('--create-key', default='no', help='Create SSH keypair', show_default=True)
@click.option('--key-path', default='/dev/null', help='Path to SSH public key.', show_default=True)
@click.option('--create-vpc', default='yes', help='Create VPC', show_default=True)
@click.option('--vpc-id', help='Specify an already existing VPC', show_default=True)
@click.option('--private-subnet-id1', help='Specify a Private subnet within the existing VPC', show_default=True)
@click.option('--private-subnet-id2', help='Specify a Private subnet within the existing VPC', show_default=True)
@click.option('--private-subnet-id3', help='Specify a Private subnet within the existing VPC', show_default=True)
@click.option('--public-subnet-id1', help='Specify a Public subnet within the existing VPC', show_default=True)
@click.option('--public-subnet-id2', help='Specify a Public subnet within the existing VPC', show_default=True)
@click.option('--public-subnet-id3', help='Specify a Public subnet within the existing VPC', show_default=True)
@click.option('--route53-hosted-zone', help='Hosted zone for accessing the environment')
@click.option('--no-confirm', is_flag=True, help='Skip confirmation prompt')
@click.option('-v', '--verbose', count=True)

def launch_env(stack_name=None,
               region=None,
               ami=None,
               bastion_instance_type=None,
               keypair=None,
               create_key=None,
               key_path=None,
               create_vpc=None,
               vpc_id=None,
               private_subnet_id1=None,
               private_subnet_id2=None,
               private_subnet_id3=None,
               public_subnet_id1=None,
               public_subnet_id2=None,
               public_subnet_id3=None,
               route53_hosted_zone=None,
               no_confirm=False,
               verbose=0):

    # Need to prompt for the R53 zone:
    if route53_hosted_zone is None:
        route53_hosted_zone = click.prompt('Hosted DNS zone for accessing the environment')

    # Create ssh key pair in AWS if none is specified
    if create_key in 'yes' and key_path in 'no':
        key_path = click.prompt('Specify path for ssh public key')
        keypair = click.prompt('Specify a name for the keypair')

    # If no keypair is not specified fail:
    if keypair is None and create_key in 'no':
        click.echo('A SSH keypair must be specified or created')
        sys.exit(1)

    # Name the keypair if a path is defined
    if keypair is None and create_key in 'yes':
        keypair = click.prompt('Specify a name for the keypair')

    # Fail on missing key_path
    if key_path in '/dev/null' and create_key in 'yes':
        key_path = click.prompt('Specify the location of the public key')

    # If no subnets are defined prompt:
    if create_vpc in 'no' and vpc_id is None:
        vpc_id = click.prompt('Specify the VPC ID')

    # If no subnets are defined prompt:
    if create_vpc in 'no' and private_subnet_id1 is None:
        private_subnet_id1 = click.prompt('Specify the first Private subnet within the existing VPC')
        private_subnet_id2 = click.prompt('Specify the second Private subnet within the existing VPC')
        private_subnet_id3 = click.prompt('Specify the third Private subnet within the existing VPC')
        public_subnet_id1 = click.prompt('Specify the first Public subnet within the existing VPC')
        public_subnet_id2 = click.prompt('Specify the second Public subnet within the existing VPC')
        public_subnet_id3 = click.prompt('Specify the third Public subnet within the existing VPC')

    # Display information to the user about their choices
    click.echo('Configured values:')
    click.echo('\tStack Name: %s' % stack_name)
    click.echo('\tAMI: %s' % ami)
    click.echo('\tRegion: %s' % region)
    click.echo('\tBastion Instance Type: %s' % bastion_instance_type)
    click.echo('\tKeypair: %s' % keypair)
    click.echo('\tCreate Key: %s' % create_key)
    click.echo('\tKey Path: %s' % key_path)
    click.echo('\tCreate VPC: %s' % create_vpc)
    click.echo('\tVPC ID: %s' % vpc_id)
    click.echo('\tPrivate Subnet ID1: %s' % private_subnet_id1)
    click.echo('\tPrivate Subnet ID2: %s' % private_subnet_id2)
    click.echo('\tPrivate Subnet ID3: %s' % private_subnet_id3)
    click.echo('\tPublic Subnet ID1: %s' % public_subnet_id1)
    click.echo('\tPublic Subnet ID2: %s' % public_subnet_id2)
    click.echo('\tPublic Subnet ID3: %s' % public_subnet_id3)
    click.echo('\tPublic Hosted Zone: %s' % route53_hosted_zone)
    click.echo("")

    if not no_confirm:
        click.confirm('Continue using these values?', abort=True)

    playbooks = ['playbooks/infrastructure.yml']

    for playbook in playbooks:
        devnull = '> /dev/null'

        if verbose > 0:
            devnull = ''

        # refresh the inventory cache to prevent stale hosts from interfering with re-running
        command = 'inventory/aws/hosts/ec2.py --refresh-cache %s' % devnull
        os.system(command)

        # remove any cached facts to prevent stale data during a re-run
        command = 'rm -rf .ansible/cached_facts'
        os.system(command)

        command = 'ansible-playbook -i inventory/aws/hosts -e \'region=%s \
        stack_name=%s \
        ami=%s \
        keypair=%s \
        create_key=%s \
        add_node=no \
        key_path=%s \
        create_vpc=%s \
        vpc_id=%s \
        private_subnet_id1=%s \
        private_subnet_id2=%s \
        private_subnet_id3=%s \
        public_subnet_id1=%s \
        public_subnet_id2=%s \
        public_subnet_id3=%s \
        bastion_instance_type=%s \
        route53_hosted_zone=%s \' %s' % (region,
                                         stack_name,
                                         ami,
                                         keypair,
                                         create_key,
                                         key_path,
                                         create_vpc,
                                         vpc_id,
                                         private_subnet_id1,
                                         private_subnet_id2,
                                         private_subnet_id3,
                                         public_subnet_id1,
                                         public_subnet_id2,
                                         public_subnet_id3,
                                         bastion_instance_type,
                                         route53_hosted_zone,
                                         playbook)

        if verbose > 0:
            command += " -" + "".join(['v']*verbose)
            click.echo('We are running: %s' % command)

        status = os.system(command)
        if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
            sys.exit(os.WEXITSTATUS(status))


if __name__ == '__main__':
    # Check for AWS access info
    if os.getenv('AWS_ACCESS_KEY_ID') is None or os.getenv('AWS_SECRET_ACCESS_KEY') is None:
        print('AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY **MUST** be exported as environment variables.')
        sys.exit(1)

    launch_env(auto_envvar_prefix='AWS_Ansible')
