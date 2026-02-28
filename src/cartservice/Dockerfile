FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder
WORKDIR /app
COPY . .
RUN dotnet restore cartservice.csproj
RUN dotnet build cartservice.csproj -c Release -o /cartservice
RUN dotnet publish cartservice.csproj -c Release -o /cartservice

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=builder /cartservice .
EXPOSE 7070
ENTRYPOINT ["./cartservice"]