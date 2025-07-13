FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Next.jsのデフォルトポート3000番を開けておく
EXPOSE 3000

CMD ["npm", "run", "dev"]