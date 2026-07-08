import os
import re
import mysql.connector


def parse_salary_range(salary_range):
    if not salary_range or salary_range.strip() == "":
        return None, None, None

    if 'Thoả thuận' in salary_range or 'Thỏa thuận' in salary_range:
        return None, None, None

    numbers = re.findall(r'\d+\.?\d*', salary_range)

    # Không có số → không biết lương
    if len(numbers) == 0:
        return None, None, None

    # Chỉ có 1 số → ví dụ "Từ 10", "Trên 15", "Lên đến 20"
    if len(numbers) == 1:
        val = float(numbers[0])
        return 0, val, val / 2

    # Có 2 số trở lên → lấy 2 số đầu làm min & max
    min_salary = float(numbers[0])
    max_salary = float(numbers[1])
    avg_salary = (min_salary + max_salary) / 2
    return min_salary, max_salary, avg_salary



def calculate_average_salary():
    conn = mysql.connector.connect(
        host=os.getenv("CRAWLER_DATABASE_HOST"),
        user=os.getenv("CRAWLER_DATABASE_USERNAME"),
        password=os.getenv("CRAWLER_DATABASE_PASSWORD"),
        database=os.getenv("CRAWLER_DATABASE_NAME")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, salary_range FROM jobs")
    rows = cursor.fetchall()

    for row in rows:
        job_id, salary_range = row
        min_salary, max_salary, avg_salary = parse_salary_range(salary_range)

        cursor.execute("""
            UPDATE jobs
            SET min_salary = %s, max_salary = %s, avg_salary = %s
            WHERE id = %s
        """, (min_salary, max_salary, avg_salary, job_id))

    conn.commit()
    cursor.close()
    conn.close()
