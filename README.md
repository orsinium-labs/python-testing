# Python testing

The repository contains exercises, code for them, and answers on the subject of testing Python apps. The goal is to cover best practices rather than basics.

The initial implementation is created for the purpose of running an internal workshop. However, I tried my best to make the code and tutorials in this repository. So, you should be able to walk yourself (or your coworkers) through these exercises without my assistance.

All questions have my answer under the spoiler. Keep in mind, though, that most of the questions (if not all of them) have multiple answers, and so if your answers differ from mine doesn't mean you're wrong.

## Prerequisites

* [Python](https://www.python.org/) 3.7+ and knowledge of how to write code on it.
* [Pytest](https://docs.pytest.org/en/latest/) and the knowledge of its basics.
* [The latest Go compiler](https://go.dev/dl/).
* [task](http://taskfile.dev/)

## Structure of exercises

Each exercise below has the following:

1. Basic description of the problem to solve.
1. What you need to do with the server (start it, stop it, start one more instance).
1. The code for my solution with additional questions about it (starting with `# Q:`).
1. Additional questions and my answers to them.

## The first implementation

We have a service that returns an HTTP response with 200 [status code](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) if it works as it should. On failure, it will return the status code 500.

Both servers are included in this repo. Start them by running `task good` and `task bad`.

Your task is to write a CLI tool that will check if the given server is healthy (returns 200). Before you do that, try answering the following questions:

<details>
  <summary>How often the tool should check if the service is alive?</summary>

  That's a trick question. The best aproach is to write a tool that runs once, does it job, and exits with a specific [exit code](https://en.wikipedia.org/wiki/Exit_status) (0 if all is good, 1 if there is a problem). That way, you don't need to worry about scheduling, fault tolerance, and memory leaks. The code will be much smaller, and easier to read and to test. Also, you'll be able to [pipe](https://en.wikipedia.org/wiki/Pipeline_(Unix)) the result into another tool. For example, to send notifications into Slack on failures. And all of that without writing a single line of code! And for scheduling, [cron](https://en.wikipedia.org/wiki/Cron) can be used, which is reliable and available out-of-the-box in any Linux. So, the answer is "my code doesn't care about scheduling".

</details>

<details>
  <summary>How server URL should be passed in the client?</summary>

  You shouldn't hardcode URL in the code. It is a dynamic value that changes depending on the environment. But how to pass it?

  1. [12factor](https://12factor.net/config) recommends to use [env vars](https://en.wikipedia.org/wiki/Environment_variable). It is the easiest way to pass values into the app if you run it inside of a [Docker](https://www.docker.com/) container. And you will run it in Docker if you need to run it in [k8s](https://kubernetes.io/), [cloud run](https://cloud.google.com/run), [fly.io](https://fly.io/), and many other places.
  1. For simple CLI tools, a better option would be to use CLI flags. That way, you can use [argparse](https://docs.python.org/3/library/argparse.html), which is in stdlib, has a nice help (invoked by running the app with `--help` flag), and supports types (env vars are always strings) and defaults. You can always add support for env vars in Docker by calling the app with something like `--url $URL`. It's a bit verbose but gets the job done.
  1. You also can use a config file. It's harder to assemble piece-by-piece, harder to pass into Docker, and harder to provide a help for. Still, the big advantage is that config files can be structured a bit better.

  For this particular case, I'll go with CLI flags because we have a CLI tool rather than a service.

  Another interesting possibility is to read the list of URLs to check from [stdin](https://en.wikipedia.org/wiki/Standard_streams#Standard_input_(stdin)). That way, you can easier pipe output of another program into this one. For example, read the list of URLs to check from a file: `cat urls.txt | python3 my_client.py`.

</details>

<details>
  <summary>When the tool should read the passed URL?</summary>

  As soon as possible. Start with reading, parsing, and validating the user input. Return the validation error to the user if the input is wrong before doing any actual logic. Pass all input as arguments into all other functions. Or, if you have too many arguments to pass everywhere, create a `Config` [dataclass](https://docs.python.org/3/library/dataclasses.html) instead of making functions with a lot of required arguments.

</details>

You can find my implementation in [client1.py](./client1.py):

1. Check it out when you finish your implementation.
1. Compare what you've done differently
1. Try to answer why it is different and which one is better
1. Answer questions in the code (starting with `# Q:`).

## The first tests

Now, we have a requirement that the client that we made will be run on the server of our clients. That means, updating it will be hard. That, in turn, means that it needs to be very reliable. So, let's write some tests.

<details>
  <summary>Which tests should you write first?</summary>

  1. Start with [integration tests](https://en.wikipedia.org/wiki/Integration_testing). At this stage, it's better to test your tool against the real server. That way, you need to make fewer assumptions about how the server works. If you start with mocks or emulators (we'll talk about them later), you test your code against a "fake server", which is based on your assumptions about how the real server works. If assumptions are wrong, your tests will pass but the tool won't actually work.
  1. These tests should be [smoke tests](https://en.wikipedia.org/wiki/Smoke_testing_(software)). Run from tests the whole app as the user will run it (or as close to it as possible). It might be slower that [unit tests](https://en.wikipedia.org/wiki/Unit_testing) covering only specific functions, but it allows to have a higher [test coverage](https://en.wikipedia.org/wiki/Fault_coverage) with less effort.

</details>

My implementation is in [test_client1.py](./test_client1.py). You can run it with `pytest test_client1.py`. Same as before, compare it with yours and answer questions.

## Testing on CI

Now, we need to run tests on CI. The problem is that the server that we ran before isn't available. All we have is, well, our tool and tests for it. Make your tests work in this situation.

Stop both servers that you had ran earlier. Do your tests fail? Why? If they fail, write tests that will work.

<details>
  <summary>Can we just run the server on CI?</summary>

  Sometimes, we can. If you have a private place where your company stores the Docker image for the server (like [artifactory](https://jfrog.com/artifactory/)), you can run it alongside of your app. It won't be that easy, though, if the server also has a lot of dependencies, like database, cache, and whatever else. Also, the server can be a complex Python app, and so will take a long time to start and require a lot of resources. And lastly, now we only have "bad" and "good" server to test, but what if we need more servers in different states? Running a new server for each test case doesn't scale well.

  It can be a good idea to start some self-contained and fast servers, though. For example, PostgreSQL or Redis, if the code that we need to test depends on them. Just ensure a good isolation of each test for others (use transactions or create a new database for each test), so they can be run in parallel. And for some complex servers, there are available emulators, which should suffice for tests. For example [fake-gcs-server](https://github.com/fsouza/fake-gcs-server) for testing code that depends on [Google Cloud Storage](https://cloud.google.com/storage).

</details>

<details>
  <summary>How to write tests that will still work?</summary>

  Many engineers would just mock the `requests.get` function. The mock would check that the expected URL is passed as the first argument and would return a fake response with `200` or `500` status code, depending on what we test. However, this approach means to make too many assumptions about how `requests` works. Assumptions may be wrong, and the tests won't catch some misuse of the library.

  Another approach is to mock not the whole library but only the response that it returns at the end for a specific HTTP request. For [requests](https://requests.readthedocs.io/en/latest/), you can use [responses](https://github.com/getsentry/responses), and for [aiohttp](https://docs.aiohttp.org/en/stable/), [aioresponses](https://github.com/pnuckowski/aioresponses).

</details>
