import sqlite3

class Service:
    def __init__(self, db_name):
        """Initialize the Service class with database connection."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_service_table()
        self.create_movie_table()

    def create_service_table(self):
        """Create the Services table if it doesn't already exist."""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Services (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Price INTEGER
            CHECK ( Price >= 0 )
        );
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def create_movie_table(self):
        """Create the Movies table if it doesn't already exist."""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Movies (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Year INTEGER CHECK (1888 <= Year AND Year <= 2025),
            Genre TEXT NOT NULL,
            Rating INTEGER CHECK(Rating >= 0 AND Rating <= 5),
            Runtime INTEGER CHECK(Runtime >= 0 AND Runtime <= 10000),
            Service_ID INTEGER,
            FOREIGN KEY (Service_ID) REFERENCES Services (ID)
        );
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def add_service(self, name, price):
        """Insert a new service into the Services table."""
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (name,))
        service = self.cursor.fetchone()

        if not service:
            insert_query = '''INSERT INTO Services (Name, Price) 
                              VALUES (?, ?)'''
            self.cursor.execute(insert_query, (name, price))
            self.conn.commit()
            print(f"Service '{name}' added to database.")
        else:
            print(f"Service '{name}' already exists.")

    def remove_service(self, name):
        """Remove a service from the Services table."""
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (name,))
        service = self.cursor.fetchone()
        if service:
            delete_query = '''DELETE FROM Services WHERE Name = ?'''
            self.cursor.execute(delete_query, (name,))
            self.conn.commit()
            print(f"Service '{name}' was removed from the database.")
        else:
            print(f"Service '{name}' was not found.")

    def add_movie(self, service_name, name, year, genre, rating, runtime):
        """Add a movie to a specific service."""
        # First, find the Service_ID for the given service name
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (service_name,))
        service = self.cursor.fetchone()

        if service:
            # Get the Service_ID
            service_id = service[0]
            try:
                insert_query = '''INSERT INTO Movies (Name, Year, Genre, Rating, Runtime, Service_ID) 
                                  VALUES (?, ?, ?, ?, ?, ?)'''
                self.cursor.execute(insert_query, (name, year, genre, rating, runtime, service_id))
                self.conn.commit()
                print(f"Movie '{name}' added to service '{service_name}'.")
            except sqlite3.IntegrityError:
                print("Incorrect values entered. Please try again.")
        else:
            print(f"Service '{service_name}' not found.")

    def remove_movie(self, service_name, movie_name):
        """Remove a movie from a specific service."""
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (service_name,))
        service = self.cursor.fetchone()
        if service_name and movie_name:
            delete_query = '''DELETE FROM Movies WHERE Name = ?'''
            self.cursor.execute(delete_query, (movie_name,))
            self.conn.commit()
            print(f"Movie '{movie_name}' was successfully removed from the service.")
        else:
            print(f"Movie '{movie_name}' not found.")

    def edit_ranking(self, service_name, movie_name, rating):
        if service_name and movie_name:
            insert_query = '''UPDATE Movies SET Rating = ? WHERE Name = ?'''
            self.cursor.execute(insert_query, (rating, movie_name))
            self.conn.commit()
            print(f"Movie '{movie_name}' rating set to {rating}.")
        else:
            print(f"Movie '{movie_name}' not found.")

    def name_check(self, service_name):
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (service_name,))
        service = self.cursor.fetchone()
        if not service:
            return False
        else:
            return True

    def movie_check(self, service_name, movie_name):
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (service_name,))
        service = self.cursor.fetchone()

        service_id = service[0]

        # Now, check if the movie exists for the current service
        self.cursor.execute('''SELECT Name FROM Movies WHERE Service_ID = ? AND Name = ?''', (service_id, movie_name))
        movie = self.cursor.fetchone()

        if not movie:
            return False
        else:
            return True

    def name_year_check(self, movie_name, movie_year):
        # Check if the movie exists in the system
        self.cursor.execute('''SELECT * FROM Movies WHERE Name = ? AND Year = ?''',
                            (movie_name, movie_year))
        movie = self.cursor.fetchone()

        if movie:
            return False
        else:
            return True


    def list_services(self):
        """List all services in the database."""
        select_query = '''SELECT * FROM Services'''
        self.cursor.execute(select_query)
        services = self.cursor.fetchall()
        if not services:
            print("No services available.")
        else:
            for service in services:
                print(f"Name: {service[1]}, Price: {service[2]}")

    def list_movies(self, service_name):
        """List all movies for a specific service."""
        self.cursor.execute('''SELECT ID FROM Services WHERE Name = ?''', (service_name,))
        service = self.cursor.fetchone()

        if service:
            service_id = service[0]
            select_query = '''SELECT * FROM Movies WHERE Service_ID = ?'''
            self.cursor.execute(select_query, (service_id,))
            movies = self.cursor.fetchall()
            if not movies:
                print(f"No movies found for service '{service_name}'.")
            else:
                for movie in movies:
                    print(f"Movie Name: {movie[1]}, Year: {movie[2]}, Genre: {movie[3]}, Rating: {movie[4]}, Runtime: {movie[5]}")
            return True
        else:
            print(f"Service '{service_name}' not found.")
            return False

    def close(self):
        """Close the database connection."""
        self.conn.close()

def main_menu():
    service = Service('test.db')

    while True:
        print("\nWelcome to the Movie Service Management System!")
        print("1. Add a new service")
        print("2. Remove a service")
        print("3. Add a movie to a service")
        print("4. Delete a movie from a service")
        print("5. List all services")
        print("6. List all movies for a selected service")
        print("7. Exit")

        option = input("Please choose an option (1-7): ")

        # Add a new service
        if option == '1':
            name = input("Enter the service name: ")
            # Check if the name is not used already
            if not service.name_check(name):
                while True:
                    try:
                        price = int(input("Enter the price of the service: "))
                        service.add_service(name, price)
                        break
                    except ValueError:
                        print("Invalid input! Please enter a valid integer for the price.")
                        continue
            else:
                print(f"Service '{name}' already exists.")

         # Remove service
        elif option == '2':
            service_name = input("Enter the name of the service you want to remove: ")
            service.remove_service(service_name)

        # Add a movie to a service
        elif option == '3':
            service_name = input("Enter the service name to add the movie to: ")
            if service.name_check(service_name):
                movie_name = input("Enter the movie name: ")

                try:
                    movie_year = int(input("Enter the movie year: "))
                except ValueError:
                    print("Invalid input! Please enter valid integers for year.")
                    continue

                if service.name_year_check(movie_name, movie_year):
                    try:
                        movie_runtime = int(input("Enter the movie runtime (in minutes): "))
                        rating_option = ""
                        while rating_option not in ('Y', 'N'):
                            rating_option = input("Do you want to add rating of the movie now? (Y/N) ")
                            if rating_option == 'Y':
                                movie_rating = int(input("Enter the movie rating (0-5): "))
                            elif rating_option == 'N':
                                movie_rating = None
                            else:
                                print("Invalid input! PLease try again.")
                    except ValueError:
                        print("Invalid input! Please enter valid integers for rating and runtime.")
                        continue
                    movie_genre = input("Enter the movie genre: ")
                    service.add_movie(service_name, movie_name, movie_year, movie_genre, movie_rating, movie_runtime)

                else:
                    print("Movie already exists.")
            else:
                print(f"Service '{service_name}' not found.")

        # Remove movie from the service
        elif option == '4':
            service_name = input("Enter the service name where the movie you want to delete is located: ")
            if service.name_check(service_name):
                movie_name = input("Enter the movie name you want to remove: ")
                service.remove_movie(service_name, movie_name)
            else:
                print(f"Service '{service_name}' not found.")

        # List all services
        elif option == '5':
            service.list_services()

        # List all movies for a service
        elif option == '6':
            service_name = input("Enter the service name to list movies for: ")

            if service.list_movies(service_name):
                # Update ranking of the movie
                update_option = ""
                print(1)
                while update_option not in ('Y', 'N'):
                    print(2)
                    update_option = input("Would you like to update the movie's rating? (Y/N) ")
                    if update_option == 'Y':
                        # update ranking
                        m_name = input("Enter the movie name you want to update ranking for: ")
                        # check if movie exists at this service
                        if service.movie_check(service_name, m_name):
                            rating = int(input("Enter the movie rating (0-5): "))
                            service.edit_ranking(service_name, m_name, rating)
                        else:
                            print(f"Movie '{m_name}' not found.")
                    elif update_option == 'N':
                        break

        # Exit the program
        elif option == '7':
            service.close()
            print("Goodbye!")
            exit(0)

        # Invalid input check
        else:
            print("Invalid choice! Please choose a valid option (1-7).")

# Run the main menu
main_menu()










