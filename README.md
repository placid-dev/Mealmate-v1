# MealMate

**MealMate** is a simple meal planning and budgeting web application built with **Python** and **Streamlit**. It helps students manage their food budget, browse available meals, log purchases, and track spending through an intuitive dashboard.

**Live Demo:** https://mymealmate.streamlit.app

---

##  About

As a university student, I noticed that many students struggle to balance their food budget while deciding what to eat every day. MealMate was built to provide a simple solution by combining meal management with budget tracking in one application.

This project is the **Minimum Viable Product (MVP)** for a larger vision of an AI-powered meal assistant.

---

## Features

-  Home page for managing available meals
-  Wallet management
-  Log meal purchases
-  Dashboard with spending analytics
-  Daily, weekly and monthly expense summaries
-  Persistent local storage using JSON files
-  Settings page for managing user information

---

## Live Demo

**Try MealMate here:**

 **https://mymealmate.streamlit.app**

---

##  Built With

- Python
- Streamlit
- JSON (Local Storage)

---

##  Project Structure

```
MealMate/
│── app.py
│── dashboard.py
│── finance.py
│── meals.py
│── settings.py
│── storage.py
│── data/
│   ├── menu.json
│   ├── wallet.json
│   ├── food_funds.json
│   └── user_profile.json
│── requirements.txt
```

---

## Running Locally

Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
```

Move into the project folder

```bash
cd <your-repository>
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

##  Why JSON Instead of a Database?

MealMate currently stores data using JSON files.

This was a deliberate design choice for Version 1 because the goal was to focus on:

- Building a complete application
- Learning Streamlit
- Designing the application logic
- Understanding state management
- Keeping the project beginner-friendly

Because of this design, the deployed application currently shares data between all users. Any changes made by one user are visible to everyone using the app.

The next version will replace JSON storage with a proper database and user authentication so that every user has their own private account and data.

---

##  Current Limitations

- Single shared JSON storage
- No user authentication
- No cloud database
- Single-user architecture
- No AI meal recommendations
- No OCR menu scanning
- No M-Pesa integration
- No notifications

These limitations are intentional and reflect the scope of the MVP.

---

## Future Improvements

Planned features include:

- User authentication
- Database integration (Supabase/PostgreSQL)
- Multi-user support
- AI-powered meal recommendations
- OCR menu scanning
- Nutrition analysis
- M-Pesa integration
- Push notifications
- Mobile application
- Personalized meal insights

---

## What I Learned

This project helped me gain hands-on experience with:

- Python application development
- Streamlit
- JSON data storage
- Modular programming
- CRUD operations
- Debugging
- Git & GitHub
- Deploying applications to Streamlit Community Cloud

---

## Project Status

**Version:** v1.0 (MVP)

MealMate v1 focuses on delivering the core budgeting and meal management experience. Future versions will introduce AI features, cloud storage, authentication, and mobile support.

---

## Author

**Edwin Kitonga**

Computer Science Student

This project was built as a learning project to improve software engineering skills while solving a real problem faced by university students.

---

## Support

If you found this project interesting, consider giving it a star on GitHub.
