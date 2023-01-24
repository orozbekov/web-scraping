import psycopg2
try:
    connection = psycopg2.connect(dbname='scraping',
                                  user='postgres',
                                  password='orozbekov',
                                  host='localhost',
                                  port="5432")
    cursor = connection.cursor()
    create_table = """CREATE TABLE module1(
                      id serial PRIMARY KEY,
                      url text NOT NULL,
                      price decimal NOT NULL,
                      currency varchar(20),
                      date date NOT NULL);"""
    cursor.execute(create_table)
    connection.commit()
    print('Таблица успешно создана...')

except psycopg2.Error as e:
    print("Ошибка при работе с PostgreSQL", e)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL завершено")

