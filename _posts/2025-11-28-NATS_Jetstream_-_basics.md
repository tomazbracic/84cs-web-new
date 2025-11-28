---
title: "NATS Jetstream – My Notes"
date: 2025-11-28
tags: [NATS, Jetstream, command line]
published: true
---


# My notes on NATS + JetStream (in plain, simple language)

> Purpose: A place where I collect what I learned while experimenting with NATS, JetStream, streams & consumers.  
> This is NOT an official guide — just my personal notes so I remember how things work.

---

I had a need at work to setup NATS with Jetstream to support some services internally. 
I worked a lot with Apache Kafka an Rabbitmq in the past, and setup NATS (streaming - not Jetstream) only once years back. So I had to "re-learn" some of the terminology. ;) 

## 🧠 What finally clicked for me

NATS alone is super fast, but messages disappear if no one is listening.  
JetStream is the part that **stores messages**, so even if my subscriber is offline, I can come back later and still read them.

So I now think of it like this:

| System | What it does |
|---|---|
| **Core NATS** | Pub/sub — fast, but no history, no replay. |
| **JetStream** | Message storage + replay + durable consumption. |

When I understood that, everything else made sense.

---

## Terminology that confused me at first

### Subject  
This is basically a routing address for messages.  
Example I used:

```
tomaz.test.debug
```

If I publish and someone is subscribed at that moment → they get the message.  
If not → message is gone. (Unless it's a JetStream message.)

---

### Stream  
This is where JetStream **stores** messages.

A stream has:
- a name (mine was `adminko-stream`)
- one or more subjects it listens to
- max retention rules if you define them

So if I publish messages *as JetStream messages*, they end up inside the stream.

---

### Consumers  
This one took me a while to get.

A consumer decides how messages are delivered to me.

There are two types that matter:

| Type | What it means in practice |
|---|---|
| **Ephemeral** | Temporary. If subscriber stops → JetStream forgets progress. |
| **Durable** | Saved position. If I stop and return later → I continue where I left off. |

Durable consumers are how you get **"only messages I missed"**, not everything.

---

### JetStream Domain  
In my setup, JetStream printed:

```
Domain: "mynats"
```

This is just the JetStream cluster name.  
If you only have one — it’s mostly just informational.

---

## Creating things — the basic order that works for me

### 1) Create a JetStream stream

```
nats stream add adminko-stream   --subjects "tomaz.test.debug"   --storage file   --retention limits   --max-msgs=-1   --max-bytes=-1   --max-age=0
```

This tells JetStream:

> Store everything published to `tomaz.test.debug`.

---

### 2) Publish messages normally (no persistence)

```
nats pub tomaz.test.debug "hello"
```

If subscriber is offline → message is gone.

---

### 3) Publish **persisted messages** (JetStream)

```
nats pub tomaz.test.debug "Hello from Tomaz MAC 19" -J
```

When this works, I see something like:

```
Stored in Stream: adminko-stream Sequence: 13 Domain: "mynats"
```

Now the message is saved.  
Now history exists.

---

### 4) Subscribe in different ways

#### Core subscription (no history)

```
nats sub tomaz.test.debug
```

Only sees messages while running.

#### Get **everything** stored

```
nats sub tomaz.test.debug --all
```

→ This replays entire stream every time  
→ Good for testing, not daily use

#### The important one: durable consumer

First create it:

```
nats consumer add adminko-stream test-adminko-consumer   --filter tomaz.test.debug   --ack explicit   --deliver all
```

Then subscribe with resume support:

```
nats sub tomaz.test.debug --durable test-adminko-consumer --ack
```

### What happens now

1. I start subscriber → I get messages
2. I stop subscriber
3. I publish N more messages
4. I start subscriber again with same durable name
5. I only get messages published while I was away

This was the “aha moment” for me.

---

## Example from my real test

```
Stored in Stream: adminko-stream Sequence: 13 Domain: "mynats"
Stored in Stream: adminko-stream Sequence: 14 Domain: "mynats"
Stored in Stream: adminko-stream Sequence: 15 Domain: "mynats"
Stored in Stream: adminko-stream Sequence: 16 Domain: "mynats"
```

Later when I came back:

```
nats sub tomaz.test.debug --durable test-adminko-consumer --ack

[#13] ... Hello from Tomaz MAC 19
[#14] ... Hello from Tomaz MAC 20
[#15] ... Hello from Tomaz MAC 21
[#16] ... Hello from Tomaz MAC 22
```

Only the gap!  
Not everything again — finally the behavior I expected.

---

## Final cheat sheet (for future me)

```
# Publish volatile message
nats pub subject "msg"

# Publish stored message
nats pub subject "msg" -J

# Create stream
nats stream add NAME --subjects "subj"

# Create durable consumer
nats consumer add STREAM durable-name --filter subj --ack explicit

# Subscribe with resume
nats sub subj --durable durable-name --ack
```

If I forget this again, hopefully I’ll find this file before I waste another two hours 😁  
Feel free to use this if it helps you too.

