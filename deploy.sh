VENV_NAME="venv_production"
WORKSPACE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

deactivate

cd $WORKSPACE
git pull || exit 0

if [ ! -d "$VENV_NAME" ]; then
    python -m venv $VENV_NAME
fi
source $VENV_NAME/bin/activate

pip freeze > pip_freeze_$(date +%Y-%m-%d--%H-%M-%S)_before.txt
pip install --upgrade pip
pip install --upgrade -r $WORKSPACE/requirements.txt
pip freeze > pip_freeze_$(date +%Y-%m-%d--%H-%M-%S)_after.txt

cd $WORKSPACE/pyquizz/
pwd

python -Wd ./manage.py collectstatic --noinput
python -Wd ./manage.py makemigrations
python -Wd ./manage.py migrate

echo -e "\e[1m"  # bold
echo -e "\e[97m" # white foreground
echo -e "\e[41m" # red background
echo ""
echo "Redemarre le site sur https://admin.alwaysdata.com/site/"
echo ""
echo -e "\e[0m" # reset all attributes
