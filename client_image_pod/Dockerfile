FROM node:8.9.4

WORKDIR /home/nodejs/app

COPY package*.json ./

RUN npm install

COPY . .

CMD ["node", "app"]

