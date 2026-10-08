# Stage 1: Build JAR with Maven & Java 21
FROM maven:3.9-eclipse-temurin-21-alpine AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B || true

COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Minimal Runtime with JRE 21 Alpine
FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache wget ca-certificates

RUN adduser -D -u 1000 appuser
USER appuser

WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8002

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD wget --quiet --tries=1 --spider http://localhost:8002/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
