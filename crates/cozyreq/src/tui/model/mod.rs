pub(crate) struct Model {
    pub(crate) running_state: RunningState,
    pub(crate) counter: i32,
}

impl Default for Model {
    fn default() -> Self {
        Model {
            running_state: RunningState::Running,
            counter: 0,
        }
    }
}

pub(crate) enum Message {
    Increment,
    Decrement,
    Quit,
}

pub(crate) fn update(model: &mut Model, msg: Message) -> Option<Message> {
    match msg {
        Message::Increment => model.counter += 1,
        Message::Decrement => model.counter -= 1,
        Message::Quit => model.running_state = RunningState::Stopped,
    }
    None
}

#[derive(PartialEq)]
pub(crate) enum RunningState {
    Running,
    Stopped,
}
