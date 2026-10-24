def test_dashboard_endpoints(client):
    # Test summary endpoint
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_expenses" in data
    assert "total_taxable" in data
    assert "total_gst" in data
    assert "total_invoices" in data

    # Test monthly expenses endpoint
    m_resp = client.get("/api/dashboard/monthly-expenses")
    assert m_resp.status_code == 200
    assert isinstance(m_resp.json(), list)

    # Test GST breakdown endpoint
    gst_resp = client.get("/api/dashboard/gst-breakdown")
    assert gst_resp.status_code == 200
    gst_data = gst_resp.json()
    assert "total_cgst" in gst_data
    assert "total_sgst" in gst_data
    assert "total_igst" in gst_data

    # Test vendor expenses endpoint
    v_resp = client.get("/api/dashboard/vendor-expenses")
    assert v_resp.status_code == 200
    assert isinstance(v_resp.json(), list)
