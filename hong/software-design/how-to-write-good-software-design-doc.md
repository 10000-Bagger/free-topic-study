# How to Write A Good Software Design Documentation

## Why write a design document?

- A design doc (also known as a technical spec) is a description of **how you plan to solve a problem**.
- A design doc is the most useful tool for making sure the right work gets done.
- The main goal of a design doc is to make you more effective by forcing you to think through the design and gather feedback from others.
- As a general rule of thumb, if you are working on a project that might take 1 engineer-month or more, you should write a design doc.
- However, different engineering teams, and even engineers within the same team, often write design docs very differently. Therefore we need to know the content, style and process of a good design doc.

## What to include in a design doc?

- A design doc describes the solution to a problem.
- To start, the following is a list of sections that you should at least consider including in your next design doc:

  - Title and People:
    - The title of your design doc,
    - The author(s) and the reviewer(s) of the doc
    - and the date this document was last updated
  - Overview
    - A high level summary that every engineer at the company should understand and use to decide if it’s useful for them to read the rest of the doc. It should be 3 paragraphs max.
  - Context
    - A description of the problem at hand. why this project is necessary, what people need to know to assess this project, and how it fits into the technical strategy, product strategy, or the team’s quarterly goals.
  - Goals and Non-Goals
    - describe the user-driven impact of your project - where your user might be another engineering team or even another technical system.
    - specify how to measure success using metrics - bonus points if you can link to a dashboard that tracks those metrics
    - Non-Goals are equally important to describe which problems you **won’t** be fixing so everyone is on the same page.
  - Milestones
    - A list of measurable checkpoints, so your PM and your manager’s manager can skim it and know roughly when different parts of the project will be done. I encourage you to break the project down into major user-facing milestones if the project is more that 1 month long.
    - Use calendar dates so you take into account unrelated delays, vacations, meetings, and so on. It should look something like this:
    ```
    Start Date: June 7, 2024
    Milestone 1 - New system MVP running in dark-mode: June 28, 2024
    Milestoen 2 - Retire old system: July 4th, 2024
    End Date: Add feature X, Y, Z to new system: July 14th, 2024
    ```
  - Existing Solution
    - In addition to describing the current implementation, you should also walk through a high level example flow to illustrate how users interact with this system and/or how data flow through it.
    - A user story is a great way to frame this. Keep in mind that your system might have different types of user with different use cases.
  - Proposed Solution
    - Some people call this the Technical Architecture section. Again, try to walk through a user story to concretize this. Feel free to include many sub-sections and diagrams.
    - Provide a big picture first, then fill in lots of details. Aim for a world where you can write this, then take a vacation on some deserted island, and another engineer on the team can just read it and implement the solution as you described.
  - Alternative Solutions

    - What else did you consider when coming up with the solution above? What are the pros and cons of the alternatives? Have you considered buying a 3rd-party solution - or using an open source one - that solves this problem as opposed to building your own?

  - Testability, Monitoring and Alerting

    - People often treat this as an afterthought or skip it all together, and it almost always comes back to bite them later when things break and they have no idea how or why.

  - Cross-Team Impact

    - How will this increase on call and dev-ops burden?
    - How much money will it cost?
    - Does it cause any latency regression to the system?
    - Does it expose any security vulnerabilities?
    - What are some negative consequences and side effect?
    - How might the support team communicate this to the customers?

  - Open Questions:
    - Any open issue that you aren’t sure about, contentious decisions that you’d like readers to weigh in on, suggested future work, and so on. A tongue-in-cheek name for the section is the “known unknowns”

## How to write it

- **Write as simply as possible**
  - **Don’t try to write like the academic papers you’ve read.** They are written to impress journal reviewers.
  - Your doc is written to describe your solution and get feedback from your teammates. You can achieve clarity by using:
    - Simple words
    - Short sentences
    - Bulleted lists and/or numbered lists
    - Concrete examples, like “User Alice connects here bank account, then …”
- **Add lots of charts and diagrams**

  - Chart can often be useful to compare several potential options, and diagrams are generally easier to parse than text. I’ve had good luck with Google Drawing for creating diagrams.
  - Tip: remember to add a link to the editable version of the diagram under the screenshot, so you can easily update it later when things inevitably change.

- **Do the Skeptic Test**

  - Before sending your design doc to others to review, take a pass at it pretending to be the reviewer.

- **Do the vacation Test**
  - If you go on a long vacation now with no internet access, can someone on your team read the doc and implement it as you intended?
  - The main goal of a design doc is not knowledge sharing, but this is a good way to evaluate for clarity so that others can actually give you useful feedback.

## Process

- Design docs help you get feedback before you waste a bunch of time implementing the wrong solution or the solution to the wrong problem.

## Reference

- [How to write a good software design doc](https://www.freecodecamp.org/news/how-to-write-a-good-software-design-document-66fcf019569c)

  - 위 내용의 번역 버전: [좋은 소프트웨어 설계문서 잘 만드는 방법](https://dev.to/itscreater/-1f7n)
