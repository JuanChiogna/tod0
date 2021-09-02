from setuptools import setup, find_packages

setup(
    name="tod0",
    version="0.6.1",
    author="kiblee",
    author_email="kiblee@pm.me",
    packages=find_packages(),
    url="https://github.com/JuanChiogna/tod0",
    license="LICENSE",
    description="Automation tool for Microsoft To-Do.",
    install_requires=[
        "prompt-toolkit",
        "pyyaml",
        "requests",
        "requests_oauthlib",
        "tzlocal",
    ],
    include_package_data=True,
    package_data={'': ['Microsoft-To-Do.ico']},
    entry_points="""
        [console_scripts]
        tod0=todocli.tod0:move_tasks_by_date
        quicktask=todocli.tod0:quick_task
    """,
    python_requires=">=3.6",
)
