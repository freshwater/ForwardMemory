
set -e

PORT=8888

PWD_=$PWD
cd $(dirname $0)

TAG=tag$RANDOM
docker build . --tag $TAG > /dev/null && docker run --rm --publish $PORT:8888 --mount type=bind,src="$PWD_",dst=/workfolder $TAG jupyter notebook --ip=0.0.0.0 --allow-root
docker rmi $TAG > /dev/null
