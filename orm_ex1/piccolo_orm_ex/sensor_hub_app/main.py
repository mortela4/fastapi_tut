if __name__ == "__main__":

    import uvicorn

    uvicorn.run("piccolo_app:app", reload=True, port=8800)

