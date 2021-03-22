import os

from config import GIT_URL_1, SOURCE_PDF_DIR


def download_repo(github_url, dst_dir):
    repo_name = github_url.split('/')[-1]
    clone_bash_command = f"git clone {github_url}.git {dst_dir}/{repo_name}"
    print(f"Run: {clone_bash_command}")
    os.system(clone_bash_command)


if __name__ == "__main__":
    download_repo(GIT_URL_1, SOURCE_PDF_DIR)  # Start Only with APT_CyberCriminal_Campagin_Collections
    # download_repo(GIT_URL_2, SOURCE_PDF_DIR)
    # download_repo(GIT_URL_3, SOURCE_PDF_DIR)
    # download_repo(GIT_URL_4, SOURCE_PDF_DIR)
#
