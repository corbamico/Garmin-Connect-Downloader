from setuptools import setup,find_packages
setup(name="gdownload",
      version="0.1.0",
      author="corbamico",
      author_email="corbamico@#163.com",
      url="http://github.com/corbamico/Garmin-Connect-Downloader",
      #packages = ["gdownload","DownloadGarmin"],
      scripts = ['DownloadGarmin.py','gdownload.py'],
      description = "Download .TCX files from the Garmin Connect web site",
      install_requires=["GcpUpLoader"]
      )
