# usage function
print_usage() {
  echo "Usage: bash path_to_script/setup.sh [-s] [-r]"
  echo "Flag Explanation: -s flag creates a superuser, -r flag runs llemr after setup finishes"
  echo ""
}

# define variables
create_superuser="false"
run_after_building="false"
count=1

# get flags
while getopts 'sr' flag; do
  case "${flag}" in
    s) create_superuser="true" ;;
    r) run_after_building="true" ;;
    *) print_usage
       exit 1 ;;
  esac
done

# run setup commands
echo "=====[Running Setup]====="

echo "[$count] Building Docker Containers---------------------------------------------- "
let "count+=1" 
docker-compose -f local.yml build

echo "[$count] Creating Necessary Tables / Performing Initial Migrations--------------- "
let "count+=1" 
docker compose -f local.yml run --rm django python manage.py migrate

echo "[$count] Loading Basic Data Fixtures--------------------------------------------- "
let "count+=1" 
docker compose -f local.yml run --rm django python manage.py loaddata core workup permissions inventory labs followup vaccine


if [ $create_superuser = "true" ]; then
  echo "[$count] Creating Superuser Account---------------------------------------------- "
  let "count+=1" 
  docker-compose -f local.yml run --rm django python manage.py createsuperuser
fi

if [ $run_after_building = "true" ] ; then
  echo "[$count] Running Llemr----------------------------------------------------------- "
  let "count+=1" 
  docker-compose -f local.yml up
fi




