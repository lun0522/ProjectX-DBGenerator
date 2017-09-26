import mysql.connector
import re

cnx = mysql.connector.connect(user='root',
                              password='password',
                              host='localhost',
                              database='paintings')
cursor = cnx.cursor(buffered=True)

add_bbox = ("INSERT INTO bounding_box"
            "(title, has_face, xlo, xhi, ylo, yhi)"
            "VALUES (%s, %s, %s, %s, %s, %s)")
add_no_face = ("INSERT INTO bounding_box"
            "(title, has_face)"
            "VALUES (%s, %s)")
query_bbox = ("SELECT has_face "
              "FROM bounding_box "
              "WHERE title=%s")


def title_to_filename(title):
    # any non-alphanumeric character will be replaced
    title = re.sub('[^0-9a-zA-Z]+', ' ', title.strip())
    if len(title) > 50:
        title = title[0:50]
    return title, title.replace(" ", "_") + ".jpg"


def filename_to_title(filename):
    return filename[0:-4].replace("_", " ")


def store_bounding_box(title, xlo, xhi, ylo, yhi):
    cursor.execute(add_bbox, (title, 1, xlo, xhi, ylo, yhi))


def denote_no_face(title):
    cursor.execute(add_no_face, (title, 0))


def bbox_did_exist(title):
    cursor.execute(query_bbox, (title, ))
    return cursor.rowcount


def bbox_has_face(title):
    cursor.execute(query_bbox, (title,))
    if cursor.rowcount > 1:
        return True
    elif cursor.rowcount == 1:
        return [has_face for (has_face, ) in cursor][0]
    else:
        raise mysql.connector.Error(msg="{} does not exist in the database!".format(title))


def commit_change():
    cnx.commit()


def cleanup():
    cursor.close()
    cnx.close()


if __name__ == "__main__":
    cleanup()