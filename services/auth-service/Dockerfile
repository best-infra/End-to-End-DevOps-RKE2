FROM node:20-alpine3.19

# Install security updates
RUN apk update && apk upgrade --no-cache

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies and clean cache
RUN npm install --omit=dev && \
    npm cache clean --force

# Copy only necessary files
COPY server.js .

EXPOSE 8001

USER node

CMD ["node", "server.js"]
