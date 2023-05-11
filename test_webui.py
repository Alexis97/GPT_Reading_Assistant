import gradio as gr
import os, json 
from functools import partial

from utils import * 

def update_text(idx, text_dict, text):
    text_dict[idx] = text

def main():
    ts = {}
    with gr.Blocks() as demo:
        t1 = gr.inputs.Textbox(lines=2, label="Text1", default='text1')
        t1.change(partial(update_text, 't1', ts), inputs=[t1])
        t2 = gr.inputs.Textbox(lines=2, label="Text2", default='text2')
        t3 = gr.inputs.Textbox(lines=2, label="Text3", default='text3')
        t4 = gr.inputs.Textbox(lines=2, label="Text4", default='text4')
    
        submit_btn = gr.Button("Submit")
    
        output = gr.outputs.Textbox(label="Output")

        # * Trigger the events
        def submit(ts):
            print (ts)
            output = ' '.join([v for k, v in ts.items()])

            return output
        submit_btn.click(
            fn=partial(submit, ts=ts),
            outputs=[output]
            )
    
    # * Launch the Gradio app
    PORT = find_free_port()
    print(f"URL http://localhost:{PORT}")
    auto_opentab_delay(PORT)
    demo.queue().launch(server_name="0.0.0.0", share=False, server_port=PORT)


if __name__ == "__main__":
    main()


