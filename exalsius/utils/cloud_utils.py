import requests


def get_aws_ubuntu_image_ami(region: str, release: str = "24.04", arch: str = "amd64"):
    """
    Get the AMI ID for a given Ubuntu release and architecture for AWS.
    """
    base_url = "https://cloud-images.ubuntu.com/locator/ec2/releasesTable"

    response = requests.get(base_url)
    response.raise_for_status()
    data = response.json()

    data = data.get("aaData", [])
    image_id = None
    for elem in data:
        # Check if element matches region, release version and architecture
        # srnbckr: there is most probably a better way to do this
        if region in elem[0] and release in elem[2] and arch in elem[3]:
            image_id = elem[-2]
            # Extract AMI ID from the href link
            if "ami-" in image_id:
                ami_start = image_id.find("ami-")
                image_id = image_id[
                    ami_start : ami_start + 21
                ]  # AMI IDs are 21 chars long including "ami-"
            break

    return image_id
