from website import create_app

app = create_app()

# If this script is run directly (instead of being imported), run the Flask application
if __name__ == "__main__":
    # Run the Flask application with debug mode enabled
    app.run(debug=True)