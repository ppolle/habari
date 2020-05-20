# Habari News Scraper

## By Peter Polle

## Description
This is a news scraping service service that is availble via a web interface and a an API.

It allows users to view access the following :
* Acces the latest news articles via the api
* Filter news articles using titles and source
* View the lates news articles in the web interface
* API token authentication

### Prerequisites

The following are needed for the application to run on a local computer:
* python version 3.6
* Django framework
* Django Rest Framework v3.11
* Bootstrap v.3
* Text editor (atom, VS code or sublime text)
* Celery & RabbitMQ
* Web browser

A crucial point to note: You will need Python version 3 and above installed on your laptop.
If you don't have it installed got to [Python.org](https://www.python.org/downloads/) to install.

## Getting Started
* Clone this repository to your local computer and install all the extensions listed in the ``requirements/common.txt`` file.
* Ensure you have python3.6 installed in your computer.
* From the terminal navigate to the cloned project folder.
* Switch to the virtual environment by entering  ```source virtual/bin/activate``` from the terminal. 
* Once inside the application, a user will be able to use the application.

## Running the tests

To run the tests, run ``python manage.py test``

## Deployment

To run local server run ``python manage.py runserver``



## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details