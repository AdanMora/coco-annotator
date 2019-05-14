<script>

export default {
  template:
    "<div><i v-tooltip.right='name' class='fa fa-x' :class='iconCurrent' :style='{ color: iconColor}' @click='click'></i><br></div>",
  name: "LockButton",
  props: {
    metadata: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      name: "Lock",
      icon: {
        enabled: "fa-lock",
        disabled: "fa-unlock"
      },
      metadataList: [],
      iconCurrent: "fa-unlock",
      exist: false,
      iconColor: 'white',
      font: '24px'
    };
  },
  methods: {
    click() {
      this.metadataList.forEach(object => {
        if (object.key.length > 0) {
          if (object.key == 'lock'){
            this.exist = true;
            if (this.iconCurrent == this.icon.enabled){
              object.value = 'false';
              this.iconCurrent = this.icon.disabled;
            }
            else{
              object.value = 'true';
              this.iconCurrent = this.icon.enabled;
            }
          }
        }
      });

      if (!this.exist) 
        this.metadataList.push({ key: "lock", value: "true" });
      this.exist = false;

      this.$parent.updateMetadata();

    },
    exportMetadata() {
      let metadata = {};

      this.metadataList.forEach(object => {
        if (object.key.length > 0) {
          if (!isNaN(object.value))
            metadata[object.key] = parseInt(object.value);
          else if (
            object.value.toLowerCase() === "true" ||
            object.value.toLowerCase() === "false"
          )
            metadata[object.key] = object.value.toLowerCase() === "true";
          else metadata[object.key] = object.value;
        }
      });

      return metadata;
    },
    loadMetadata() {
      if (this.metadata != null) {
        for (var key in this.metadata) {
          if (!this.metadata.hasOwnProperty(key)) continue;
          if (key === this.exclude) continue;

          let value = this.metadata[key];

          if (value == null) value = "";
          else value = value.toString();

          if (key == 'lock' && value == 'true') {
            this.iconCurrent = this.icon.enabled;
            this.exist = true;
          }

          this.metadataList.push({ key: key, value: value });
        }
        if (!this.exist) 
           this.iconCurrent = this.icon.disabled;
        this.exist = false;
      }
    }
  }, 
  watch: {
    metadata() {
      this.metadataList = []
      this.loadMetadata();
    }
  },
  created() {
    this.loadMetadata();
  }
};
</script>
