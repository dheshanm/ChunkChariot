# A Simple Flask File Uploader

This is a simple file uploader built with Flask. It allows users to upload files to the server.

## Features

- **Authentication**: Users can sign up and log in to the application.
- **Form-based file upload**: Users can upload files to the server by filling out a form.
- **Chunked File Upload**: Users can upload large files in chunks. [^1] [^2] [^3]
- **File Management**: Users can download and delete files they have uploaded.

[^1]: [codecalamity.com](https://codecalamity.com/upload-large-files-fast-with-dropzone-js/)

[^2]: [codecalamity.com](https://codecalamity.com/uploading-large-files-by-chunking-featuring-python-flask-and-dropzone-js/)

[^3]: [StackOverflow](https://stackoverflow.com/questions/44727052/handling-large-file-uploads-with-flask)

## Tech Stack

### Languages and Frameworks

- Python
- Flask (Web Framework)
- PostgreSQL (Database)

### Libraries

- Flask-WTF (Form Handling)
- Flask-Login (User Authentication)
- Bootstrap (Frontend Framework)
- Dropzone.js (File Upload)

## Screenshots

### Home Page

![Home Page](docs/assets/screenshots/home-signed-in.png)

### Upload Page

![Upload Page](docs/assets/screenshots/upload-form.png)

### Upload History

![Upload History](docs/assets/screenshots/upload-history.png)
