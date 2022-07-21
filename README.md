# Python testing

The repository contains exercises, code for them, and answers on the subject of testing Python apps. The goal is to cover best practices and motivation behind them rather than basics.

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
1. The code for my solution with additional questions about it (starting with `# Q:`). Answers are decoded with [ROT13](https://en.wikipedia.org/wiki/ROT13). Use `codecs.decode('some text', 'rot13')` to decode them.
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

My implementation is in [test_client1.py](./test_client1.py). You can run it with `task test1`. Same as before, compare it with yours and answer questions.

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

  A better approach is to mock not the whole library but only the response that it returns at the end for a specific HTTP request. For [requests](https://requests.readthedocs.io/en/latest/), you can use [responses](https://github.com/getsentry/responses), and for [aiohttp](https://docs.aiohttp.org/en/stable/), [aioresponses](https://github.com/pnuckowski/aioresponses).

</details>

You can find my implementation in [test_client2.py](./test_client2.py). Use `python3 -m pytest test_client2.py`is to run it.

## Proxy

For this exercise, I want you to take the role of the developers of the server. There is a new requirement from the business. We need to modify the server so that it can take a role of a "proxy". Such server should be considered healthy only if another server, which it points to, is also healthy. In other words, when we check health of the server, it may answer "yeah, I'm fine, but you should also check this guy".

<details>
  <summary>How to make this change without breaking the tool we developed earlier?</summary>

  A possible solution is to use a [URL redirect](https://en.wikipedia.org/wiki/URL_redirection). All we need to do that on the server side is to return a special code 301 and a header `Location` that will point to another server. In Go (which we use for the server), it can be done by calling [http.Redirect](https://pkg.go.dev/net/http#Redirect).

</details>

<details>
  <summary>Will the client still work after the change? Why?</summary>

  Well, it should. Thanks to a good standardization of HTTP and thank to us for using it, the HTTP library you picked (requests, httpx, aiohttp) should follow redirects by default, or at least support it as an optional flag. For instance, for requests, the flag is `follow_redirects`, and it's `True` by default.

  If the library does not follow redirects by default (or you explicitly made it so), the change still shouldn't break old versions of the tool, because 3xx codes are considered a success. Only 4xx indicates a client error and 5xx indicates a server error. In that case, the client will be broken only if you explicitly checked for 200 in the return code. So, if instead of `resp.status_code == 200` you check `resp.ok`, all should be fine.

</details>

<details>
  <summary>Shouldn't the client be a strict as possible?</summary>

  You may have explicitly disabled redirects and allowed only 200 responses in your implementation of the client by design. And it would be a good idea in some scenarios, when you have a full control over both sides (the one that produces the status code and the one that uses it). When you have some assertions about the system, it's often a good idea to explicitly state them as early in your pipeline as possible. This approach is known as "[fail-fast](https://en.wikipedia.org/wiki/Fail-fast)".

  In our case, however, we don't have full control over the server, and the client and server may evolve and be released independently. In that case, a better-suited approach is "[be liberal in what you accept from others](https://en.wikipedia.org/wiki/Robustness_principle)". In other words, do not make too many assumptions, only the necessary ones.

  This dichotomy is also known as "[open-world](https://en.wikipedia.org/wiki/Open-world_assumption) and [closed-world](https://en.wikipedia.org/wiki/Closed-world_assumption) assumption". There is no single answer to what is better, it highly depends on the situation, the problem you're solving, and the trade-offs you're ready to make.

</details>

## Tests for proxy

We already had 2 possible states for the server: "good" and "bad". Now, we also have "proxy". There are also some states we, perhaps, haven't tested for. What if we can't resolve DNS name of the server? What if it's unreachable? What if the server responded but timed out while sending the HTTP headers? There are many corner-cases we want to test if we want the client to be reliable.

<details>
  <summary>How to make it easy to add new test cases?</summary>

  [Table-driven tests](https://en.wikipedia.org/wiki/Data-driven_testing)! I already did it in my [test_client2.py](./test_client2.py) by using [pytest.mark.parametrize](https://docs.pytest.org/en/6.2.x/parametrize.html), so no surprise here. But why? First of all, it's less code, and so the tests are easier to read and understand. But what's the most important is that now it's easy to add new test cases. Humans are lazy, and nobody likes writing tests. More friction you have for adding a new test case, fewer tests you will have at the end. And if adding a new test case means adding one short line `(given, expected)`, you will have a good test coverage in no time.

</details>

<details>
  <summary>What about integration tests? How many do we need?</summary>

  Usually, adding a new integration test means not just one more test case but much more effort. And the execution time is much slower that for unit-tests that don't make any actual network requests. In our case, for each state we want to test, we have to run a new instance of the server. And, as I said before, a real-world server may require a lot of resources and other services. As we'll see in exercises below, we often can afford only one instance of the server for integration tests. So, you won't have much of them.

  The idea of having fewer integration tests than unit tests is known as "[test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)". The idea of pyramid and naming are controversial, and people all the time try to come up with a better structure. Still, the core idea usually stays the same: you have tests of different granularity and complexity, and the focus should be on keeping tests simple, fast, and reproducible.

</details>

Write tests covering the new state. You can start the proxy server by running `task proxy`. It will be started on the same port as the "good" server was running. My implementation is available in [test_client3.py](./test_client3.py) and can be ran as `python3.9 -m pytest test_client3.py`.

## Unexpected changes

Let's say, the server team wasn't so mindful about our tool. They made a breaking change. For instance, now the server requires `User-Agent: healthcheck` to be present in all requests. What's even worse, the change wasn't clearly communicated, and the new version of the server was released without letting us know.

<details>
  <summary>Will our tests detect the issue?</summary>

  Well, yes and no. Yes because integration tests will indeed detect the issue. No because we don't run integration tests on CI, and there is no guarantee that anyone will runn the tests locally with the new version of the server before we release it on the prod.

</details>

<details>
  <summary>Who's to blame for the issue?</summary>

  [No blame culture](https://www.davidsonmorris.com/no-blame-culture/) means that, well, we don't blame anyone ever for any issues. The goal is to avoid people being silent about issues they introduce, out of fear being blamed for it, or other negative effects impacting them. And also if you start blaming people around, you'll get a sticky idea "I'm working with idiots", which is harmful for your mental state.

  You should, however, always ask yourself what went wrong and how to prevent a similar issue happening again. In this case, we have a combination of at least 3 factors:

  1. The change was breaking, and we should avoid breaking changes.
  1. The change wasn't clearly communicated.
  1. We don't run integration tests. So, what's even the point of having them?

  Let's try to fix the last one.

</details>

<details>
  <summary>Can we make integration tests a part of CI?</summary>

  We already touched on the subject a few times, the first time when we decided to skip integration tests on CI. Now we learned the hard way that tests either run on CI, or there is no point of having them at all. So, we **have to** have all tests running on CI, and we definitely should have some integration tests.

  But what if the server is hard to run on CI? Many big companies solve it by triggering from CI a deployment of the whole project (both the server and the healthcheck tool) in a special production-like environment. In this environment, you can run integration tests as well as just manually click buttons and see if your changes work. It should be done before each release, and preferrably also before merging each MR touching the code.

</details>

<details>
  <summary>How many instances of the server we need on CI?</summary>

  The answer is "one". If we start a new server for each state we want to test, it doesn't scale well.

</details>

<details>
  <summary>What integration tests are the most important ones?</summary>

  If to pick "the best" integration test, it should be the one that tests the [happy path](https://en.wikipedia.org/wiki/Happy_path). Exceptions are (surprise!) exceptional. Most of the servers we check most of the time are "good" ones, so testing the integration with a "good" server ensures that the tool works most of the time.

</details>

<details>
  <summary>Can we test multiple states with a single server?</summary>

  Sure, why not. Quite often, you'll be able to run multiple integration tests on a single instance of the server. For example, if you need to test a registration form, you may register many different users with different fake emails, each time checking for a different behavior.

  Our case is a bit different, though. A server is only in one state at the same time, either healthy or not. So, in the current implementation, we can test only one state of the server. But we can do more if we modify the server a bit. Let's make it accept a request parameter (`?state=healthy` or `?state=down`) that will indicated which state the server should pretend to be in.

  The idea is similar to how you fire alarm works. Do you have a fire alarm? You should. If you do, go and look at it. It has a little red LED that blips time-to-time. It's a happy path. The fire alarm works and apparently doesn't scream that there is smoke (because, I hope, there is none). Now, put on ear plugs and hold the big button for 3 seconds. The fire alarm (if it's not broken) will make a sound like it does when it detects smoke. In other words, by pressing the button you ask the fire alarm to emulate the invalid state.

  CO2 gas sensors go even further. When you press a button to test it, it will not just check if sound work, but actually trigger the sensor, as it gets triggered when there is gas. In other words, instead of pretending for the user that there is a problem, it actually emulates a problem. And you can do something similar with your tests. Instead of asking the server to pretend that it's in a bad state, ask it to actually get into invalid state. Or put it there. For instance, go and remove its database.

</details>

## Making fewer requests

Often, the server will be not something you can deploy locally, but rather a third-party service that is up and running all the time somewhere else. For example, you may use [virustotal API](https://developers.virustotal.com/reference/overview) to check for viruses all files users upload on your server. That means, each API request costs money, can be rate limited, can be slow, and sometimes even the whole server will be down. And you don't want these limitations to affect your work. Also, your team and the project grow, so everyone all the time runs tests, triggers CI, and each test run sends hundreds of requests.

The goal of this exercise is to reduce how many (and how often) requests we send to the server without reducing how many integration tests we have.

<details>
  <summary>Can we just mock everything?</summary>

  We kinda can. We can turn most of our integration tests into unit tests by mocking all requests for them as we did before. Then we, apparently, have only a few integration tests, but it can be fine if the API we test is well maintained by smart engineers and almost never gets changed. A bigger issue is that now we have a lot of mocks. It's a lot of effort to create them, to maintain them, to make sure that all assumptions we made about the API when writing mocks are correct.

</details>

<details>
  <summary>Is there a way to generate mocks?</summary>

  I'm glad I asked! There is a famous and cool library for Ruby called [vcr](https://github.com/vcr/vcr). In fact, so cool and famous that it has a lot of clones and inspired projects for many other programming languages. The one for Python is called [vcrpy](https://github.com/kevin1024/vcrpy). VCR tracks all HTTP requests you do during the tests. The first time you run tests, the will do HTTP requests to the API as usual. VCR will track the requests and store all responses in a cache file. The next time your run tests, instead of doing actual requests, VCR will check that the request hasn't changed and return the cached responses. In other words, it automatically generates mocks for HTTP requests.

  Another option, as we covered before, is to use emulators. For example, instead of sending requests to Google Cloud Storage and pay for each test, you can use [fake-gcs-server](https://github.com/fsouza/fake-gcs-server). You can think of it as a mock for the whole service, in some sense.

</details>

<details>
  <summary>When you should use generated mocks? When you shouldn't?</summary>

  Use autogenerated mocks when at least one is true:

  1. You pay for requests.
  1. Requests are rate-limited.
  1. Requests are slow.
  1. You send a lot of requests from tests.

  Don't use autogenerated mocks when it's just a few tests for a simple API for which you can make your own mock in no time.

</details>

<details>
  <summary>Should I track the cache with git?</summary>

  You definitely shouldn't if the requsts or responses contain secrets or sensitive information. For example, I use VCR in [bux SDK](https://github.com/orsinium-labs/bux). it's a public repo, and tests send my private token in each request. I want no chance that it will leak.

  If you don't track the cache, it will be responsibility for each developer to keep the cache up to date. That means, depending on the cache age, results may differ for different developers for the same tests. And it can be a bit of a headache. On CI, there are also solutions to store cache outside of the repository, but you again need to think in advance how often the cache should be updated. So, if this is an issue for your project, store the cache in git.

  In other cases, it is controversial. IMHO, git should track only the human-written code, and everything that can be generated from that code shouldn't be tracked but generated on demand. For instance, you don't commit `__pycache__` for your code because it can be generated from the source code.

</details>

Change the integration tests so that they cache HTTP responses, or generate mocks for the server in some other way. My implementation is available as [test_client4.py](./test_client4.py) and can be ran using `task test4`.

## Summary

There are some of topics that we've covered:

1. Integration tests vs unit tests
1. Running tests on CI.
1. Mocks.
1. Emulators.
1. Table-driven tests.
1. Backward-compatibility.
1. Running services for tests.
1. Autogenerated mocks.
1. Using third-party APIs in tests.

Things that aren't covered but also important:

1. [Test behavior, not implementation](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html)
1. [Property-based testing](https://increment.com/testing/in-praise-of-property-based-testing/) with [hypothesis](https://hypothesis.readthedocs.io/en/latest/)
1. [Design by contract](https://deal.readthedocs.io/basic/motivation.html) with [deal](https://deal.readthedocs.io/).
