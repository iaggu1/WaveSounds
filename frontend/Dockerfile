FROM node:20-bookworm-slim

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
ARG API_INTERNAL_URL=http://backend:8000
ENV API_INTERNAL_URL=${API_INTERNAL_URL}
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
