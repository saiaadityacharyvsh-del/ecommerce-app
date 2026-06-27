# MyShop

Flask e-commerce application with user, admin, and superadmin flows.

## Features

- User registration and login
- Product browsing and shopping cart
- Razorpay payment flow
- Order history and PDF invoices
- Admin product and order management
- Superadmin approval and dashboard

## Project Structure

```text
.
|-- app.py
|-- config.py
|-- requirements.txt
|-- .env.example
|-- static/
|-- templates/
`-- utils/
```

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`

## Environment Variables

Create a `.env` file based on `.env.example`.

```env
SECRET_KEY=your-secret-key
DEBUG=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
DB_PATH=smartcart.db
```

## Notes

- `smartcart.db` is ignored by Git.
- Uploaded files under `static/upload/` are ignored by Git.
- For PythonAnywhere, create the `.env` file on the server.
