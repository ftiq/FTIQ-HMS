/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { useState, onMounted, useRef, Component } = owl;

export class AcsWebCam extends Component {
    static props = { "*": { optional: true } }
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.acsWebcamVideo = useRef("acsWebcamVideo");
        this.acsWebcamCanvas = useRef("acsWebcamCanvas");

        this.state = useState({
            resModel: null,
            resId: null,
            imageField: "image_1920",
            imageData: "",
            user_data: {},
            cameraReady: false,
            snapshotTaken: false,
            popup: {
                show: false,
                message: "",
                type: "info"
            },
        });

        onMounted(async () => {
            const ctx = await this.acsGetContextInfo();
            if (ctx) {
                this.state.resModel = ctx.resModel;
                this.state.resId = Array.isArray(ctx.resId) ? ctx.resId[0] : ctx.resId;
                await this.acsGetUserInfo(this.state.resModel, this.state.resId);
            }
            await this.acsStartCamera();
        });
    }

    async acsGetContextInfo() {
        try {
            const resModel =
                this.props?.action?.res_model ||
                this.props?.action?.context?.active_model;
            const resId =
                this.props?.action?.context?.active_id ||
                this.props?.action?.context?.active_ids;
            if (!resModel || !resId) return;
            return { resModel, resId };
        } catch (e) {
            console.error(e);
        }
    }

    async acsGetUserInfo(resModel, resId) {
        console.log("\n Webcam ResModel ----- ", resModel);
        console.log("\n Webcam ResId ----- ", resId);
        try {
            const [userData] = await this.orm.read(resModel, [resId], ["name", "image_1920"]);
            if (!userData) return;
            userData.user_name = userData.name;
            userData.user_img = userData.image_1920;
            this.state.user_data = userData;
        } catch (e) {
            console.error(e);
        }
    }

    async acsStartCamera() {
        const video = this.acsWebcamVideo.el;
        const mediaConfig = { video: true };
        
        try {
            let stream;
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                stream = await navigator.mediaDevices.getUserMedia(mediaConfig); // Modern API
            } else if (navigator.getUserMedia) {
                stream = await new Promise((resolve, reject) => {
                    navigator.getUserMedia(mediaConfig, resolve, reject); // Standard legacy API
                });
            } else if (navigator.webkitGetUserMedia) {
                stream = await new Promise((resolve, reject) => {
                    navigator.webkitGetUserMedia(mediaConfig, resolve, reject); // WebKit-prefixed
                });
            } else if (navigator.mozGetUserMedia) {
                stream = await new Promise((resolve, reject) => {
                    navigator.mozGetUserMedia(mediaConfig, resolve, reject); // Mozilla-prefixed
                });
            } else {
                throw new Error("getUserMedia is not supported in this browser");
            }
            if ("srcObject" in video) {
                video.srcObject = stream;
            } else {
                video.src = window.URL.createObjectURL(stream);
            }
            await video.play();
            this._videoStream = stream;
            this.state.cameraReady = true;
        } catch (e) {
            console.error("Camera error:", e);
            this.state.cameraReady = false;
        }
    }

    acsTakeSnapshot() {
        if (!this.state.cameraReady) return;
        const video = this.acsWebcamVideo.el;
        const canvas = this.acsWebcamCanvas.el;
        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, 800, 600);
        this.state.imageData = canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, "");
        this.state.snapshotTaken = true;
    }

    async acsSaveImage() {
        if (!this.state.snapshotTaken) return;
        try {
            await this.orm.call(this.state.resModel, "acs_webcam_update_image",
                [this.state.resId],
                { image_field: this.state.imageField, image_data: this.state.imageData }
            );
            this.acsStopCamera();
            history.back();
        } catch (err) {
            console.error("Error saving image:", err);
        }
    }

    acsStopCamera() {
        if (this._videoStream) {
            this._videoStream.getTracks().forEach(track => track.stop());
        }
        this.state.cameraReady = false;
        this.state.snapshotTaken = false;
    }

    acsShowPopup(type="info") {
        this.state.popup.message = "Are you sure you want to cancel?";
        this.state.popup.type = type;
        this.state.popup.show = true;
        document.body.classList.add('popup-open');
    }

    acsClosePopup = () => {
        this.state.popup.show = false;
        this.state.popup.message = "";
        document.body.classList.add('popup-open');
    }

    acsCancel() {
        this.acsStopCamera();
        history.back();
    }
}

AcsWebCam.template = "acs_webcam.AcsWebCam";
registry.category("actions").add("AcsWebCam", AcsWebCam);