# Laravel Multi-Panel Application

This is a Laravel application structured to support multiple panels:
- **User Website**
- **Vendor Panel**
- **Admin Panel**

## Project Structure

### Routes
- `routes/web.php`: Routes for the User Website.
- `routes/vendor.php`: Routes for the Vendor Panel (prefixed with `/vendor`).
- `routes/admin.php`: Routes for the Admin Panel (prefixed with `/admin`).

### Controllers
- `app/Http/Controllers`: User Website controllers.
- `app/Http/Controllers/Vendor`: Vendor Panel controllers.
- `app/Http/Controllers/Admin`: Admin Panel controllers.

### Models
- `app/Models/User`: Model for Users.
- `app/Models/Vendor`: Model for Vendors.
- `app/Models/Admin`: Model for Admins.

## Setup

1.  **Clone the repository.**
2.  **Install dependencies**:
    ```bash
    composer install
    npm install
    ```
3.  **Environment Setup**:
    - Copy `.env.example` to `.env`.
    - Set `DB_CONNECTION=sqlite` (or your preferred database).
    - Run `php artisan key:generate`.
    - Create `database/database.sqlite` if using SQLite.
4.  **Run Migrations**:
    ```bash
    php artisan migrate
    ```
5.  **Serve the Application**:
    ```bash
    php artisan serve
    ```

## Access

- User Website: `http://localhost:8000/`
- Vendor Panel: `http://localhost:8000/vendor`
- Admin Panel: `http://localhost:8000/admin`
