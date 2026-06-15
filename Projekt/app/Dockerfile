# Etap 1: Budowanie aplikacji przy użyciu Maven
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
# Pobranie zależności bez budowania kodu (przyspiesza kolejne budowania dzięki cache)
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

# Etap 2: Uruchomienie aplikacji
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
# Kopiujemy tylko gotowy plik .jar z poprzedniego etapu
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]