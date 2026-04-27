import uvicorn


def main() -> None:
    uvicorn.run("workshop_api.main:app", host="127.0.0.1", port=9090, reload=True)


if __name__ == "__main__":
    main()
