import gradio as gr
from run.newTest import inference,parse_args_as_parameter
# from seg_core import Segmentation
# from seg_core_512 import Segmentation as Seg512


# seg = Segmentation(device='cuda')
# seg512 = Seg512(device='cuda')


# def TestSegmentation(input_image):
#     # icc_profile = input_image.info.get('icc_profile')
#     img = seg.execute(pil_image=input_image, device='cpu', model_key=seg.MODEL_KEY_ANY)
#     return gr.Image(img), gr.Text(seg.classification_class)

# def TestSegmentation512(input_image):
#     # icc_profile = input_image.info.get('icc_profile')
#     img = seg512.execute(pil_image=input_image, device='cpu', model_key=seg.MODEL_KEY_PERSON)
#     return gr.Image(img)

def testInspyReNet(input_image):
    input_image.save("image.jpg")
    args = parse_args_as_parameter(source="image.jpg")
    inference(args)
    return gr.Image("output/image.png")

with gr.Blocks() as demo:
    with gr.Tab('InspyRenet'):
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(type="pil")
                submit_button = gr.Button("Submit")
            with gr.Column():
                output_image = gr.Image(type="pil")
                # output_text = gr.Textbox(label="Selected Model")
                
            submit_button.click(
                testInspyReNet,
                inputs= input_image,
                outputs= output_image
            )


demo.launch(server_name='0.0.0.0',server_port=8200)        


