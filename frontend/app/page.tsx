'use client'

import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'

interface OrderHeader {
  OrderID: number
  OrderNumber: string
  CustomerName: string
  CustomerAddress: string
  OrderDate: string
  DueDate: string | null
  TotalAmount: number
  TaxAmount: number
  SubTotal: number
  Status: string
  CreatedAt: string
  UpdatedAt: string
}

interface OrderDetail {
  DetailID: number
  OrderID: number
  LineNumber: number
  ProductName: string
  ProductCode: string
  Quantity: number
  UnitPrice: number
  LineTotal: number
}

interface Order {
  header: OrderHeader
  details: OrderDetail[]
}

export default function Home() {
  const [orders, setOrders] = useState<OrderHeader[]>([])
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState<Order | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const fetchOrders = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/orders`)
      setOrders(response.data)
    } catch (err) {
      console.error('Error fetching orders:', err)
    }
  }, [])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  const handleFileUpload = async (file: File) => {
    setIsUploading(true)
    setError(null)
    setSuccess(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSuccess(`Invoice ${response.data.data.orderNumber} extracted successfully!`)
      await fetchOrders()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to process invoice')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleViewOrder = async (orderId: number) => {
    try {
      const response = await axios.get(`${API_URL}/orders/${orderId}`)
      setSelectedOrder(response.data)
      setEditData(response.data)
      setIsModalOpen(true)
      setIsEditing(false)
    } catch (err) {
      setError('Failed to load order details')
    }
  }

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (!editData) return

    try {
      await axios.put(`${API_URL}/orders/${editData.header.OrderID}`, editData)
      setSuccess('Order updated successfully!')
      setIsEditing(false)
      await fetchOrders()
      
      // Refresh the selected order
      const response = await axios.get(`${API_URL}/orders/${editData.header.OrderID}`)
      setSelectedOrder(response.data)
      setEditData(response.data)
    } catch (err) {
      setError('Failed to update order')
    }
  }

  const handleDelete = async (orderId: number) => {
    if (!confirm('Are you sure you want to delete this order?')) return

    try {
      await axios.delete(`${API_URL}/orders/${orderId}`)
      setSuccess('Order deleted successfully!')
      setIsModalOpen(false)
      await fetchOrders()
    } catch (err) {
      setError('Failed to delete order')
    }
  }

  const handleCancel = () => {
    if (selectedOrder) {
      setEditData(selectedOrder)
    }
    setIsEditing(false)
  }

  const updateHeaderField = (field: string, value: any) => {
    if (!editData) return
    setEditData({
      ...editData,
      header: {
        ...editData.header,
        [field]: value,
      },
    })
  }

  const updateDetailField = (detailId: number, field: string, value: any) => {
    if (!editData) return
    setEditData({
      ...editData,
      details: editData.details.map((detail) =>
        detail.DetailID === detailId ? { ...detail, [field]: value } : detail
      ),
    })
  }

  return (
    <div className="container">
      <h1 style={{ color: 'white', marginBottom: '2rem', fontSize: '2.5rem', textAlign: 'center' }}>
        Invoice Extraction App
      </h1>

      {error && (
        <div className="error" onClick={() => setError(null)}>
          {error}
        </div>
      )}

      {success && (
        <div className="success" onClick={() => setSuccess(null)}>
          {success}
        </div>
      )}

      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>Upload Invoice</h2>
        <div
          className={`upload-area ${isUploading ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {isUploading ? (
            <div className="loading">
              <div className="spinner"></div>
              <span style={{ marginLeft: '1rem' }}>Processing invoice...</span>
            </div>
          ) : (
            <>
              <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
                Drag and drop an invoice image here, or click to select
              </p>
              <input
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="file-input"
              />
              <label htmlFor="file-input" className="btn btn-primary">
                Select File
              </label>
            </>
          )}
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>Extracted Invoices</h2>
        {orders.length === 0 ? (
          <p style={{ color: '#6c757d', textAlign: 'center', padding: '2rem' }}>
            No invoices extracted yet. Upload an invoice to get started.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Order Number</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Total Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.OrderID}>
                  <td>{order.OrderNumber}</td>
                  <td>{order.CustomerName}</td>
                  <td>{new Date(order.OrderDate).toLocaleDateString()}</td>
                  <td>${order.TotalAmount.toFixed(2)}</td>
                  <td>
                    <span
                      style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '12px',
                        fontSize: '0.875rem',
                        backgroundColor:
                          order.Status === 'Completed'
                            ? '#d4edda'
                            : order.Status === 'Pending'
                            ? '#fff3cd'
                            : '#f8d7da',
                        color:
                          order.Status === 'Completed'
                            ? '#155724'
                            : order.Status === 'Pending'
                            ? '#856404'
                            : '#721c24',
                      }}
                    >
                      {order.Status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-primary"
                      style={{ padding: '0.5rem 1rem', marginRight: '0.5rem' }}
                      onClick={() => handleViewOrder(order.OrderID)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && selectedOrder && (
        <div className="modal" onClick={() => !isEditing && setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2>Order Details</h2>
              <button
                className="btn btn-secondary"
                onClick={() => setIsModalOpen(false)}
                style={{ padding: '0.5rem 1rem' }}
              >
                Close
              </button>
            </div>

            {isEditing ? (
              <>
                <div className="form-group">
                  <label>Order Number</label>
                  <input
                    type="text"
                    className="input"
                    value={editData?.header.OrderNumber || ''}
                    onChange={(e) => updateHeaderField('OrderNumber', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Customer Name</label>
                  <input
                    type="text"
                    className="input"
                    value={editData?.header.CustomerName || ''}
                    onChange={(e) => updateHeaderField('CustomerName', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Customer Address</label>
                  <textarea
                    className="input"
                    rows={3}
                    value={editData?.header.CustomerAddress || ''}
                    onChange={(e) => updateHeaderField('CustomerAddress', e.target.value)}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Order Date</label>
                    <input
                      type="date"
                      className="input"
                      value={editData?.header.OrderDate || ''}
                      onChange={(e) => updateHeaderField('OrderDate', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Due Date</label>
                    <input
                      type="date"
                      className="input"
                      value={editData?.header.DueDate || ''}
                      onChange={(e) => updateHeaderField('DueDate', e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Subtotal</label>
                    <input
                      type="number"
                      step="0.01"
                      className="input"
                      value={editData?.header.SubTotal || 0}
                      onChange={(e) => updateHeaderField('SubTotal', parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Tax Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      className="input"
                      value={editData?.header.TaxAmount || 0}
                      onChange={(e) => updateHeaderField('TaxAmount', parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Total Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      className="input"
                      value={editData?.header.TotalAmount || 0}
                      onChange={(e) => updateHeaderField('TotalAmount', parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Status</label>
                    <select
                      className="input"
                      value={editData?.header.Status || ''}
                      onChange={(e) => updateHeaderField('Status', e.target.value)}
                    >
                      <option value="Pending">Pending</option>
                      <option value="Completed">Completed</option>
                      <option value="Cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>

                <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Line Items</h3>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Line #</th>
                      <th>Product Name</th>
                      <th>Product Code</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th>Line Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {editData?.details.map((detail) => (
                      <tr key={detail.DetailID}>
                        <td>
                          <input
                            type="number"
                            className="input"
                            style={{ width: '60px' }}
                            value={detail.LineNumber}
                            onChange={(e) => updateDetailField(detail.DetailID, 'LineNumber', parseInt(e.target.value))}
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            className="input"
                            value={detail.ProductName}
                            onChange={(e) => updateDetailField(detail.DetailID, 'ProductName', e.target.value)}
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            className="input"
                            value={detail.ProductCode}
                            onChange={(e) => updateDetailField(detail.DetailID, 'ProductCode', e.target.value)}
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            step="0.01"
                            className="input"
                            style={{ width: '100px' }}
                            value={detail.Quantity}
                            onChange={(e) => updateDetailField(detail.DetailID, 'Quantity', parseFloat(e.target.value))}
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            step="0.01"
                            className="input"
                            style={{ width: '100px' }}
                            value={detail.UnitPrice}
                            onChange={(e) => updateDetailField(detail.DetailID, 'UnitPrice', parseFloat(e.target.value))}
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            step="0.01"
                            className="input"
                            style={{ width: '100px' }}
                            value={detail.LineTotal}
                            onChange={(e) => updateDetailField(detail.DetailID, 'LineTotal', parseFloat(e.target.value))}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                  <button className="btn btn-primary" onClick={handleSave}>
                    Save Changes
                  </button>
                  <button className="btn btn-secondary" onClick={handleCancel}>
                    Cancel
                  </button>
                </div>
              </>
            ) : (
              <>
                <div style={{ marginBottom: '2rem' }}>
                  <h3>Order Information</h3>
                  <p><strong>Order Number:</strong> {selectedOrder.header.OrderNumber}</p>
                  <p><strong>Customer:</strong> {selectedOrder.header.CustomerName}</p>
                  <p><strong>Address:</strong> {selectedOrder.header.CustomerAddress}</p>
                  <p><strong>Order Date:</strong> {new Date(selectedOrder.header.OrderDate).toLocaleDateString()}</p>
                  {selectedOrder.header.DueDate && (
                    <p><strong>Due Date:</strong> {new Date(selectedOrder.header.DueDate).toLocaleDateString()}</p>
                  )}
                  <p><strong>Subtotal:</strong> ${selectedOrder.header.SubTotal.toFixed(2)}</p>
                  <p><strong>Tax:</strong> ${selectedOrder.header.TaxAmount.toFixed(2)}</p>
                  <p><strong>Total:</strong> ${selectedOrder.header.TotalAmount.toFixed(2)}</p>
                  <p><strong>Status:</strong> {selectedOrder.header.Status}</p>
                </div>

                <h3 style={{ marginBottom: '1rem' }}>Line Items</h3>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Line #</th>
                      <th>Product Name</th>
                      <th>Product Code</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th>Line Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedOrder.details.map((detail) => (
                      <tr key={detail.DetailID}>
                        <td>{detail.LineNumber}</td>
                        <td>{detail.ProductName}</td>
                        <td>{detail.ProductCode}</td>
                        <td>{detail.Quantity}</td>
                        <td>${detail.UnitPrice.toFixed(2)}</td>
                        <td>${detail.LineTotal.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                  <button className="btn btn-primary" onClick={handleEdit}>
                    Edit
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(selectedOrder.header.OrderID)}
                  >
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
