import sqlite3

class Service:
    def __init__(self, db_name):
        """Initialize the Service class with database connection."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create the Services table if it doesn't already exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Services (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Price INTEGER
            CHECK ( Price >= 0 )
        );
        ''')

        self.cursor.execute('''
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
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TV_Series (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Genre TEXT NOT NULL,
            Rating INTEGER CHECK(Rating >= 0 AND Rating <= 5)       
            );
        ''')

        # Linked table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Series_Service(
            Series_Name TEXT NOT NULL,
            Service_Name TEXT NOT NULL,
            FOREIGN KEY (Series_Name) REFERENCES TV_Series (Name) ON DELETE CASCADE,
            UNIQUE (Series_Name, Service_Name)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Season (
            Series_Name TEXT NOT NULL,
            Season_Number INTEGER,
            Year INTEGER,
            Episodes_Number INTEGER,                
            Service_Name TEXT NOT NULL,
            FOREIGN KEY (Series_Name) REFERENCES TV_Series (Name) ON DELETE CASCADE,
            FOREIGN KEY (Service_Name) REFERENCES Services (Name) ON DELETE CASCADE,
            UNIQUE (Series_Name, Season_Number)
            );       
        ''')

        self.conn.commit()

    # Manage Services functions
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

    # Manage Movies functions
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
                    print(
                        f"Movie Name: {movie[1]}, Year: {movie[2]}, Genre: {movie[3]}, Rating: {movie[4]}, Runtime: {movie[5]}")
            return True
        else:
            print(f"Service '{service_name}' not found.")
            return False

    def get_service_id(self, service_name):
        self.cursor.execute('''SELECT ID FROM Services WHERE Name=?''', (service_name,))
        service = self.cursor.fetchone()
        if service:
            service_id = service[0]
            return service_id
        return False

    # Manage TV_Series functions
    def add_series(self, service_name, series_name, genre, rating):
        """Add TV_Series to a specific server"""
        service_id = self.get_service_id(service_name)
        if service_id:
            # check if exists in TV_Series table
            self.cursor.execute('''SELECT * FROM TV_Series WHERE Name =?''', (series_name,))
            exists = self.cursor.fetchone()
            if not exists:
                self.cursor.execute('''INSERT INTO TV_Series (Name, Genre, Rating) VALUES (?, ?, ?)''',
                                    (series_name, genre, rating))
                self.conn.commit()

            # insert data into linked table (does not matter if tv_series already existed in the system)
            self.cursor.execute('''INSERT INTO Series_Service (Series_Name, Service_Name) VALUES (?,?)''',
                                (series_name, service_name))
            self.conn.commit()
            return f"{series_name} was successfully added to {service_name}"
        return "Service not found"

    # remove series from all the services
    def remove_series(self, service_name, series_name):
        """Remove TV_Series from a specific server"""
        service_id = self.get_service_id(service_name)
        if service_id:
            self.cursor.execute('''SELECT * FROM Series_Service WHERE Series_Name =? AND Service_Name=?''',
                                (series_name, service_name))
            exists = self.cursor.fetchall()
            if exists:
                self.cursor.execute('''DELETE FROM Series_Service WHERE Series_Name =? AND Service_Name=?''',
                                    (series_name, service_name))
                self.cursor.execute('''DELETE FROM Season WHERE Series_Name =? AND Service_Name=?''',
                                    (series_name, service_name))
                self.conn.commit()

                # check if any other  service has series available, if not remove series from tv_series table
                self.cursor.execute('''SELECT * FROM Series_Service WHERE Series_Name=? AND Service_Name=?''',
                                    (series_name, service_name))
                series_left = self.cursor.fetchall()
                if not series_left:
                    self.cursor.execute('''DELETE FROM TV_Series WHERE Name=?''', (series_name,))
                    self.conn.commit()
                return f"{series_name} was successfully removed from the system"

            else:
                return f"{series_name} was not found on {service_name}."

        return "Service not found"

    def remove_series_from_service(self, series_name, service_name):
        service_id = self.get_service_id
        if service_id:
            # check if series exist at this service
            self.cursor.execute('''SELECT * FROM Series_Service WHERE Series_Name =? AND Service_Name =?''',
                                (series_name, service_name))
            series_service_exist = self.cursor.fetchone()
            if series_service_exist:
                self.cursor.execute('''DELETE FROM Series_Service WHERE Series_Name=? AND Service_Name =?''',
                                    (series_name, service_name))
                self.cursor.execute('''DELETE FROM Season WHERE Series_Name =? AND Service_Name =?''',
                                    (series_name, service_name))
                self.conn.commit()
            else:
                return f"{series_name} does not exist on {service_name}."
        return "Service not found"

    def add_season(self, service_name, series_name, season_number, year, episodes_number):
        service_id = self.get_service_id(service_name)
        # check if service exists
        if service_id:
            # check if there are no other records of series_name AND season_number
            self.cursor.execute('''SELECT * FROM Season WHERE Series_Name =? AND Season_Number =?''',
                                (series_name, season_number))
            exists = self.cursor.fetchone()
            if not exists:
                # check if series were added to service_name already
                self.cursor.execute('''SELECT * FROM Series_Service WHERE Series_Name =? AND Service_Name =?''',
                                    (series_name, service_name))
                series_service_exist = self.cursor.fetchone()
                if series_service_exist:
                    self.cursor.execute(
                        '''INSERT INTO Season (Series_Name, Season_Number, Year, Episodes_Number, Service_Name) VALUES (?,?,?,?,?)''',
                        (series_name, season_number, year, episodes_number, service_name))
                    self.conn.commit()
                    return f"{series_name} season {season_number} was successfully added to {service_name}"
                return f"{series_name} was not found on {service_name}. To add season to series make sure to add series to the service beforehand."
            else:
                season_service = exists[4]
                return f"{series_name} season {season_number} already exists on {season_service}."
        return f"{service_name} does not exist on the system."

    def remove_season(self, series_name, season_number):
        self.cursor.execute('''SELECT * FROM Season WHERE Series_Name=? AND Season_Number=?''',
                            (series_name, season_number))
        exists = self.cursor.fetchone()
        if exists:
            self.cursor.execute('''DELETE FROM Season WHERE Series_Name=? AND Season_Number=?''',
                                (series_name, season_number))
            self.conn.commit()
            return f"Season {season_number} was successfully removed."
        return f"Season {season_number} is not on the system."

    def add_ranking_series(self, series_name, rating):
        self.cursor.execute('''SELECT * FROM TV_Series WHERE Name =?''')
        exists = self.cursor.fetchone()
        if exists:
            self.cursor.execute('''UPDATE TV_Series SET Rating =? WHERE Name =?''', (rating, series_name))
            return f"Rating for {series_name} was set to {rating}."
        return f"Series {series_name} was not found."

    def list_series(self, service):
        # list all the seasons of a series
        self.cursor.execute('''SELECT Series_Name, Season_Number, Year, Episodes_Number FROM Season WHERE Service_Name = ?''', (service,))
        lst_series = self.cursor.fetchall()
        if lst_series:
            result = []
            for series in lst_series:
                result.append(series)
            return result
        return f"{service} has no TV_Series available."

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
        print("5. Add series to a service")
        print("6. Add season to series of a service")
        print("7. Remove series from the service")
        print("8. Remove a season of series")
        print("9. List all services")
        print("10. List all movies for a selected service")
        print("11. List all the series for a selected service")
        print("12. Exit")

        option = input("Please choose an option (1-12): ")

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
                                while True:
                                    try:
                                        movie_rating = int(input("Enter the movie rating (0-5): "))
                                        if 0 <= movie_rating <= 5:
                                            break  # Exit the loop if the input is valid
                                        else:
                                            print("Please enter a rating between 0 and 5.")
                                    except ValueError:
                                        print("Invalid input. Please enter an integer between 0 and 5.")

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

        # Add series
        elif option == '5':
            service_name = input("Enter the service name to add the TV Series to: ")
            if service.name_check(service_name):
                series_name = input("Enter the name of the TV Series you want to add: ")
                # check if series are already in tv_series table
                genre = input("Enter genre: ")
                while True:
                    try:
                        rating = int(input("Enter the series rating (0-5): "))
                        if 0 <= rating <= 5:
                            break
                        else:
                            print("Please enter a rating between 0 and 5.")
                    except ValueError:
                        print("Invalid input. Please enter an integer between 0 and 5.")

                while True:
                    try:
                        season = int(input("Enter season number: "))
                        if type(season) is int:
                            break
                        else:
                            print("Please enter season number(integer).")
                    except ValueError:
                        print("Invalid input. Please enter an integer.")

                year = input("Enter year of release: ")

                while True:
                    try:
                        episodes = int(input("Enter number of episodes: "))
                        if type(episodes) is int:
                            break
                        else:
                            print("Please enter number of episodes(integer).")
                    except ValueError:
                        print("Invalid input. Please enter an integer.")
                print(service.add_series(service_name, series_name, genre, rating))
                print(service.add_season(service_name, series_name, season, year, episodes))
            else:
                print(f"Service '{service_name}' not found.")

        # Add a season
        elif option == '6':
            service_name = input("Enter the service name to add the TV Series to: ")
            series_name = input("Enter the name of the TV Series you want to add: ")
            # check if the series exists on the system already, if no - error message
            season = input("Add season (number): ")
            year = input("Enter year of release: ")
            episodes = input("Enter number of episodes: ")
            print(service.add_season(service_name, series_name, season, year, episodes))

        # Remove series
        elif option == '7':

            service_name = input("Enter the service you want to remove series from: ")
            series_name = input("Enter series name which you want to remove: ")
            answer = input("Do you want to remove all the seasons? (Y/N): ")
            if answer == "Y":
                service.remove_series(service_name, series_name)
                print("Series were successfully removed from the service.")
            elif answer == "N":
                season_remove = input("Enter number of the season you want to remove: ")
                service.remove_season(series_name, season_remove)
                print(f"Season {season_remove} was successfully removed.")
            else:
                print("Invalid input. Please try again.")

        # Remove season
        elif option == '8':
            series_name = input("Enter the series to remove season from: ")
            exists = service.name_check(service_name)
            if exists:
                season = input("Enter season number you want to remove: ")
                print(service.remove_season(series_name, season))
            else:
                print(f"{series_name} do not exist on the system.")

        # List all services
        elif option == '9':
            service.list_services()

        # List all movies for a service
        elif option == '10':
            service_name = input("Enter the service name to list movies for: ")

            if service.list_movies(service_name):
                # Update ranking of the movie
                update_option = ""
                while update_option not in ('Y', 'N'):
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

        # List the TV_Series for the service
        elif option == '11':
            service_name = input("Enter the service name to list TV Series for: ")
            exists = service.name_check(service_name)
            if exists:
                result = (service.list_series(service_name))
                if result: 
                    for series in result:
                        print(f"Name: {series[0]}, Season: {series[1]}, Year: {series[2]}, Episodes: {series[3]}")
            else:
                print(f"Service '{service_name}' not found.")

        # Exit the program
        elif option == '12':
            service.close()
            print("Goodbye!")
            exit(0)

        # Invalid input check
        else:
            print("Invalid choice! Please choose a valid option (1-12).")


# Run the main menu
main_menu()
