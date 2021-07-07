import random
import datetime
import json

# !!! prior to running script delete all workups of pk>4, all demographics of pk>1 and all patients of pk>6 !!!

path = "osler//fixtures//"

with open(path+"extra_patients.json", "r") as p:
    patients = json.load(p)

with open(path+"extra_workups.json", "r") as w:
    workups = json.load(w)

with open(path+"extra_demographics.json", "r") as d:
    demographics = json.load(d)

with open(path+"extra_encounters.json", "r") as e:
    encounters = json.load(e)


names = ['Calvin Lawson', 'Perry Garcia', 'Gertrude Schneider', 'Forrest Cain', 'Margaret Dunn', 'Sadie Richards', 'Nora Leonard', 'Vicki Castro', 'Everett Kennedy', 'Ervin Padilla', 'Chad Boone', 'Kelly Lamb', 'Tara Martinez', 'Erick Cobb', 'Eunice Adkins', 'Julie Sims', 'Blanca Gonzales', 'Kristin Henry', 'Amelia Harper', 'Terrence Howard', 'Leonard Barnett', 'Winston Mckenzie', 'Armando Lindsey', 'Virginia Matthews', 'Phillip Saunders', 'Leigh Gilbert', 'Catherine Sanchez', 'Carol Weber', 'Brett Palmer', 'Paulette Bass', 'Leroy West', 'Howard Ryan', 'Rachael Swanson', 'Amos Ramsey', 'Sergio Vaughn', 'Pat Brady', 'Bernadette Cruz', 'Wayne Thomas', 'Tyler Love', 'Claude Soto', 'Jacquelyn Burton', 'Kenneth Zimmerman', 'Hubert Peterson', 'Virgil Morris', 'Jacqueline Miller', 'Rachel Hanson', 'Danielle Douglas', 'Billy Fleming', 'Enrique Vega',
         'Rosa Mccarthy', 'Alison Henderson', 'Jeremy Oliver', 'Melanie Marsh', 'Bertha Garza', 'Alexis Roberts', 'Andrew Park', 'Alicia Ortega', 'Monique Patterson', 'Delia Burns', 'Dewey Weaver', 'Marsha Walton', 'Willie Goodwin', 'Geoffrey Parsons', 'Salvador Morales', 'Susan Jones', 'Clay Neal', 'Craig Mullins', 'Brandi Banks', 'Meredith Gonzalez', 'Ruben Holland', 'Norma Barton', 'Adrian Ramos', 'Jackie Herrera', 'Henrietta Lawrence', 'Kimberly Perkins', 'Orville Franklin', 'Velma Gardner', 'Melinda Watts', 'Christina Mills', 'Heidi Maxwell', 'Gregory Pena', 'Melba Fox', 'Bill Robinson', 'Rudy Jennings', 'Rudolph Sandoval', 'Delbert Olson', 'Kate Lucas', 'Jamie Foster', 'Violet Maldonado', 'Maxine Powers', 'Bobbie Wise', 'Norman Ball', 'Gwendolyn Ellis', 'Ivan Grant', 'Agnes Pearson', 'Nettie Parks', 'Elijah Phelps', 'Kristy Mason', 'Owen Jensen', 'Kay Lee']

ethnicities = ["White", "Black or African American", "American Indian or Alaska Native",
               "Asian", "Native Hawaiian or Other Pacific Islander", "Hispanic or Latino", "Other"]

conditions = ["Hypertension", "Hypertension", "Hypertension", "Hypertension", "Hypertension", "Back Pain",
              "Back Pain", "Back Pain", "Back Pain", "Back Pain", "High Cholesterol", "High Cholesterol",
              "High Cholesterol", "High Cholesterol", "Diabetes", "Diabetes", "Heart Disease", "Arthritis",
              "Depression", "Cancer", "Asthma", "Obesity"]

# num_encounters = 200
num_patients = 100
wu_per_patient = 10


def random_date_in_range(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y')
    end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y')
    secs = random.randint(0, int((end_date - start_date).total_seconds()))
    new_date = start_date + datetime.timedelta(seconds=secs)
    return str(new_date.date())


def load_fixtures():
    pk = 5

    for p in range(6, num_patients):
      patient = patients[0].copy()
      patient["pk"] = p
      f = patient["fields"].copy()
      name = names[p].split(" ")
      f["first_name"] = name[0]
      f["last_name"] = name[1]
      f["date_of_birth"] = random_date_in_range("01/01/1940", "12/31/2020")
      g = random.randint(0, 1)
      if(g == 0):
          f["gender"] = "Male"
      else:
          f["gender"] = "Female"
      f["ethnicities"] = random.sample(ethnicities, random.randint(1, 3))
      patient["fields"] = f
      patients.append(patient)
      num_workups = random.randint(1, wu_per_patient)

      demographic = demographics[10].copy()
      demographic["pk"] = p
      f = demographic["fields"].copy()
      f["patient"] = p  # link demographic to patient
      f["chronic_conditions"] = random.sample(conditions, random.randint(1, 3))
      demographic["fields"] = f
      demographics.append(demographic)
      

      for w in range(num_workups):
          workup = workups[4].copy()
          workup["pk"] = pk
          f = workup["fields"].copy()
          f["bp_sys"] = str(random.randint(100, 180))
          f["patient"] = p  # link demographic to patient
          date_written = random_date_in_range("01/01/2018", "07/06/2021")
          f["written_datetime"] = date_written
          f["last_modified"] = date_written
          f["encounter"] = pk
          workup["fields"] = f
          workups.append(workup)


          #create encounters for each workup
          encounter = encounters[1].copy()
          encounter["pk"] = pk
          e = encounter["fields"].copy()
          e["order"] = pk
          e["patient"] = p
          e["clinic_day"] = date_written
          encounter["fields"] = e
          encounters.append(encounter)

          pk += 1


load_fixtures()

with open(path+"extra_patients.json", "w") as p:
    json.dump(patients, p, indent=4)

with open(path+"extra_workups.json", "w") as w:
    json.dump(workups, w, indent=4)

with open(path+"extra_demographics.json", "w") as d:
    json.dump(demographics, d, indent=4)

with open(path+"extra_encounters.json", "w") as e:
    json.dump(encounters, e, indent=4)
