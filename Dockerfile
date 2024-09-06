FROM python:3.9.19-alpine

WORKDIR /code

RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools \
    # pillow dependencies
    jpeg-dev zlib-dev   freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p .logs

CMD [ "python", "./main.py" ]
