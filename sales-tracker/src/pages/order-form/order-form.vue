<template>
  <view class="page">
    <text class="page-title">{{ orderId ? '编辑订单' : '新建订单' }}</text>

    <view class="section-label">客户信息</view>
    <view class="field">
      <text class="field-label">客户姓名</text>
      <input class="field-input" v-model="form.name" placeholder="必填" />
    </view>
    <view class="field-row">
      <view class="field">
        <text class="field-label">联系电话</text>
        <input class="field-input" v-model="form.phone" />
      </view>
      <view class="field">
        <text class="field-label">来源渠道</text>
        <input class="field-input" v-model="form.source" placeholder="例如：抖音私信" />
      </view>
    </view>
    <view class="field-row">
      <view class="field">
        <text class="field-label">经济状况</text>
        <input class="field-input" v-model="form.financial_status" placeholder="预算/付款方式" />
      </view>
      <view class="field">
        <text class="field-label">AI微信</text>
        <input class="field-input" v-model="form.ai_wechat" />
      </view>
    </view>

    <view class="section-label">匹配与阶段</view>
    <view class="field">
      <text class="field-label">匹配车型</text>
      <picker :range="productOptions" :value="productIndex" @change="onProductChange">
        <view class="field-input picker-input">{{ productOptions[productIndex] }}</view>
      </picker>
    </view>
    <view class="field">
      <text class="field-label">客户阶段</text>
      <picker :range="stageOptions" :value="stageIndex" @change="onStageChange">
        <view class="field-input picker-input">{{ stageOptions[stageIndex] }}</view>
      </picker>
    </view>
    <view class="field">
      <text class="field-label">归属销售跟单猿</text>
      <picker :range="assignedOptions" :value="assignedIndex" @change="onAssignedChange">
        <view class="field-input picker-input">{{ assignedOptions[assignedIndex] || '-- 选择销售跟单猿 --' }}</view>
      </picker>
    </view>

    <template v-if="stageIndex >= 6">
      <view class="section-label">成交信息</view>
      <view class="field-row">
        <view class="field">
          <text class="field-label">成交金额</text>
          <input class="field-input" type="digit" v-model="form.amount" />
        </view>
        <view class="field">
          <text class="field-label">签约日期</text>
          <picker mode="date" :value="form.signed_at" @change="(e) => (form.signed_at = e.detail.value)">
            <view class="field-input picker-input">{{ form.signed_at || '选择日期' }}</view>
          </picker>
        </view>
      </view>
    </template>

    <template v-if="stageIndex >= 7">
      <view class="section-label">交付 / 售后</view>
      <view class="field-row">
        <view class="field">
          <text class="field-label">交付日期</text>
          <picker mode="date" :value="form.delivered_at" @change="(e) => (form.delivered_at = e.detail.value)">
            <view class="field-input picker-input">{{ form.delivered_at || '选择日期' }}</view>
          </picker>
        </view>
        <view class="field">
          <text class="field-label">售后状态</text>
          <picker :range="aftersalesOptions" :value="aftersalesIndex" @change="onAftersalesChange">
            <view class="field-input picker-input">{{ aftersalesOptions[aftersalesIndex] }}</view>
          </picker>
        </view>
      </view>
      <view class="field">
        <text class="field-label">售后备注</text>
        <textarea class="field-input" v-model="form.aftersales_notes" :maxlength="-1" />
      </view>
    </template>

    <view class="section-label">备注</view>
    <view class="field">
      <textarea class="field-input" v-model="form.notes" placeholder="跟进记录、客户偏好等" :maxlength="-1" />
    </view>
    <text class="msg error" v-if="msg">{{ msg }}</text>

    <view class="actions">
      <button v-if="orderId" class="btn-danger" @click="onDelete">删除</button>
      <button class="btn-primary" @click="onSave">保存</button>
    </view>

    <tab-bar current="/pages/order-form/order-form" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'
import {
  getOrders,
  createOrder,
  updateOrder,
  deleteOrder,
  getSalesProducts,
  getSalesList,
  ensureLoggedIn,
  CUSTOMER_STAGES,
} from '@/utils/api.js'

const AFTERSALES = ['质保中', '质保结束', '维修中']

export default {
  components: { TabBar },
  data() {
    return {
      orderId: '',
      currentUser: null,
      products: [],
      salesUsers: [],
      productIndex: 0,
      stageIndex: 0,
      assignedIndex: -1,
      aftersalesIndex: 0,
      msg: '',
      form: {
        name: '',
        phone: '',
        source: '',
        financial_status: '',
        ai_wechat: '',
        product_id: null,
        stage: 'initial_chat',
        assigned_to: '',
        amount: 0,
        signed_at: '',
        delivered_at: '',
        aftersales_status: '质保中',
        aftersales_notes: '',
        notes: '',
      },
    }
  },
  computed: {
    productOptions() {
      return ['未选择', ...this.products.map((p) => p.name)]
    },
    stageOptions() {
      return CUSTOMER_STAGES.map((s, i) => `${i + 1}. ${s.label}`)
    },
    assignedOptions() {
      return this.salesUsers.map((u) => u.username)
    },
    aftersalesOptions() {
      return AFTERSALES
    },
  },
  onLoad(options) {
    this.orderId = options && options.id ? options.id : ''
    this.init()
  },
  methods: {
    async init() {
      // "搞订单"是操作，不是逛——没登录就直接弹去登录页，带上 redirect 让登录
      // 成功后跳回这个页面（连带 ?id= 一起，不会把"正要编辑哪条订单"弄丢）。
      const redirectUrl = `/pages/order-form/order-form${this.orderId ? `?id=${this.orderId}` : ''}`
      this.currentUser = await ensureLoggedIn(redirectUrl)
      if (!this.currentUser) return
      try {
        const [products, salesUsers] = await Promise.all([getSalesProducts(), getSalesList()])
        this.products = products
        this.salesUsers = salesUsers
      } catch (e) {
        this.products = []
        this.salesUsers = []
      }
      if (this.orderId) {
        await this.loadExisting()
      } else if (this.currentUser && this.currentUser.role === 'operator') {
        this.assignedIndex = this.assignedOptions.indexOf(this.currentUser.username)
      }
    },
    async loadExisting() {
      try {
        const orders = await getOrders()
        const o = orders.find((x) => x.id === this.orderId)
        if (!o) return
        this.form = {
          name: o.name,
          phone: o.phone || '',
          source: o.source || '',
          financial_status: o.financial_status || '',
          ai_wechat: o.ai_wechat || '',
          product_id: o.product_id || null,
          stage: o.stage,
          assigned_to: o.assigned_to,
          amount: o.amount || 0,
          signed_at: o.signed_at ? String(o.signed_at).slice(0, 10) : '',
          delivered_at: o.delivered_at ? String(o.delivered_at).slice(0, 10) : '',
          aftersales_status: o.aftersales_status || '质保中',
          aftersales_notes: o.aftersales_notes || '',
          notes: o.notes || '',
        }
        this.productIndex = o.product_id ? this.products.findIndex((p) => p.id === o.product_id) + 1 : 0
        this.stageIndex = CUSTOMER_STAGES.findIndex((s) => s.key === o.stage)
        this.assignedIndex = this.assignedOptions.indexOf(o.assigned_to)
        this.aftersalesIndex = AFTERSALES.indexOf(o.aftersales_status || '质保中')
      } catch (e) {
        this.msg = '加载订单失败：' + e.message
      }
    },
    onProductChange(e) {
      this.productIndex = Number(e.detail.value)
      this.form.product_id = this.productIndex > 0 ? this.products[this.productIndex - 1].id : null
    },
    onStageChange(e) {
      this.stageIndex = Number(e.detail.value)
      this.form.stage = CUSTOMER_STAGES[this.stageIndex].key
    },
    onAssignedChange(e) {
      this.assignedIndex = Number(e.detail.value)
      this.form.assigned_to = this.assignedOptions[this.assignedIndex]
    },
    onAftersalesChange(e) {
      this.aftersalesIndex = Number(e.detail.value)
      this.form.aftersales_status = AFTERSALES[this.aftersalesIndex]
    },
    async onSave() {
      const payload = {
        ...this.form,
        name: this.form.name.trim(),
        amount: Number(this.form.amount) || 0,
        signed_at: this.form.signed_at || null,
        delivered_at: this.form.delivered_at || null,
      }
      if (!payload.name) {
        this.msg = '请填写客户姓名'
        return
      }
      if (!payload.assigned_to) {
        this.msg = '请选择归属销售跟单猿'
        return
      }
      this.msg = '保存中...'
      try {
        if (this.orderId) {
          await updateOrder(this.orderId, payload)
        } else {
          await createOrder(payload)
        }
        // home 是 tabBar 页面，只能用 switchTab 跳，redirectTo/navigateTo 对
        // tabBar 页面不生效。
        uni.switchTab({ url: '/pages/home/home' })
      } catch (e) {
        this.msg = '保存失败：' + e.message
      }
    },
    onDelete() {
      uni.showModal({
        title: '确定删除这条订单吗？',
        success: async (res) => {
          if (!res.confirm) return
          try {
            await deleteOrder(this.orderId)
            uni.switchTab({ url: '/pages/home/home' })
          } catch (e) {
            this.msg = '删除失败：' + e.message
          }
        },
      })
    },
  },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 200rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.page-title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 24rpx;
  display: block;
}
.section-label {
  font-size: 22rpx;
  color: var(--ink-soft);
  margin: 28rpx 0 16rpx;
  font-weight: 600;
}
.field {
  flex: 1;
  margin-bottom: 20rpx;
}
.field-row {
  display: flex;
  gap: 16rpx;
}
.field-label {
  font-size: 22rpx;
  color: var(--ink-soft);
  display: block;
  margin-bottom: 8rpx;
}
.field-input {
  width: 100%;
  box-sizing: border-box;
  padding: 20rpx 22rpx;
  border-radius: var(--radius-md);
  background: var(--card-bg);
  border: 1px solid var(--line);
  font-size: 27rpx;
  color: var(--ink);
}
.picker-input {
  color: var(--ink);
}
.msg { font-size: 23rpx; margin-top: 8rpx; display: block; }
.msg.error { color: var(--danger); }
.actions {
  display: flex;
  gap: 16rpx;
  margin-top: 32rpx;
}
.actions button {
  flex: 1;
  border-radius: var(--radius-md);
  font-size: 28rpx;
  font-weight: 600;
  padding: 20rpx 0;
  border: none;
}
.btn-primary {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
}
.btn-danger {
  background: var(--danger-soft);
  color: var(--danger);
  flex: 0.6;
}
</style>
